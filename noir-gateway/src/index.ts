import { Hono, Context, Next } from 'hono';
import { cors } from 'hono/cors';

type Bindings = {
  DB: D1Database;
  STORAGE: R2Bucket;
  API_KEY: string;
};

type Env = { Bindings: Bindings };

const app = new Hono<Env>();

app.use('*', cors());

// Authentication Middleware
app.use('*', async (c: Context<Env>, next: Next) => {
  if (c.req.path === '/' || c.req.path === '/health') return await next();
  const auth = c.req.header('Authorization');
  if (auth !== `Bearer ${c.env.API_KEY}`) {
    return c.json({ error: 'Unauthorized' }, 401);
  }
  await next();
});

app.get('/', (c: Context<Env>) => c.text('Noir Sovereign Gateway v14.0 ACTIVE'));
app.get('/health', (c: Context<Env>) => c.json({ status: 'ok', version: '14.0' }));

// --- AGENT ENDPOINTS ---

app.post('/agent/register', async (c: Context<Env>) => {
  const data = await c.req.json();
  const { device_id, agent, stats } = data;
  await c.env.DB.prepare(
    "INSERT INTO agents (device_id, name, last_seen, stats) VALUES (?, ?, datetime('now'), ?) ON CONFLICT(device_id) DO UPDATE SET name=excluded.name, last_seen=excluded.last_seen, stats=excluded.stats"
  ).bind(device_id, agent, JSON.stringify(stats)).run();
  return c.json({ status: 'ok' });
});

app.all('/agent/poll', async (c: Context<Env>) => {
  const device_id = (c.req.query('device_id') || 'UNKNOWN') as string;
  const client_type = (c.req.query('client_type') || 'main') as string;
  let stats = null;

  if (c.req.method === 'POST') {
    try {
      const body = await c.req.json();
      stats = body.stats;
    } catch {}
  }
  
  // Update activity timestamp and stats if provided
  if (stats) {
    await c.env.DB.prepare(
      "INSERT INTO agents (device_id, name, last_seen, stats) VALUES (?, 'Agent', datetime('now'), ?) ON CONFLICT(device_id) DO UPDATE SET last_seen=excluded.last_seen, stats=excluded.stats"
    ).bind(device_id, JSON.stringify(stats)).run();
  } else {
    await c.env.DB.prepare(
      'UPDATE agents SET last_seen = CURRENT_TIMESTAMP WHERE device_id = ?'
    ).bind(device_id).run();
  }

  // Fetch pending commands with client_type awareness
  // v17.2 optimization: Background service only pulls 'shell' commands to avoid swallowing 'vision' tasks
  let query = "SELECT id, action FROM commands WHERE (target_device = ? OR target_device IS NULL) AND status = 'pending'";
  if (client_type === 'service') {
    query += " AND (action LIKE '%\"type\":\"shell\"%' OR action LIKE '%\"action\":\"shell\"%')";
  }
  query += " LIMIT 5";

  const cmds = await c.env.DB.prepare(query).bind(device_id).all();
  const results = cmds.results as unknown as { id: string; action: string }[];
  
  if (results.length > 0) {
    const ids = results.map(r => r.id);
    await c.env.DB.prepare(
      `UPDATE commands SET status = 'sent' WHERE id IN (${ids.map(() => '?').join(',')})`
    ).bind(...ids).run();
  }
  
  return c.json({ 
    status: 'ok',
    commands: results.map(r => ({ command_id: r.id, action: JSON.parse(r.action) })) 
  });
});

app.post('/agent/result', async (c: Context<Env>) => {
  const data = await c.req.json();
  const { command_id, device_id, telemetry } = data;
  
  // v17.2: Atomic Multi-Operation via D1 Batching
  const statements = [
    c.env.DB.prepare("UPDATE commands SET status = 'done', result = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?").bind(JSON.stringify(data), command_id)
  ];

  if (telemetry && device_id) {
    statements.push(
      c.env.DB.prepare("UPDATE agents SET stats = ?, last_seen = datetime('now') WHERE device_id = ?").bind(JSON.stringify(telemetry), device_id)
    );
  }
  
  await c.env.DB.batch(statements);
  return c.json({ status: 'ok' });
});

app.post('/agent/upload', async (c: Context<Env>) => {
  const body = await c.req.parseBody();
  const device_id = (c.req.query('device_id') || body.device_id || 'UNKNOWN') as string;
  const file = body.file as unknown as File;
  const ext = file.name.split('.').pop() || 'png';
  const key = `ss_${Date.now()}.${ext}`;
  
  await c.env.STORAGE.put(key, await file.arrayBuffer(), {
    httpMetadata: { contentType: file.type || 'image/png' }
  });
  
  await c.env.DB.prepare(
    "INSERT OR IGNORE INTO agents (device_id, name) VALUES (?, 'Agent')"
  ).bind(device_id).run();

  await c.env.DB.prepare(
    'UPDATE agents SET last_screenshot = ? WHERE device_id = ?'
  ).bind(key, device_id).run();
  
  return c.json({ ok: true, key });
});

// --- DASHBOARD ENDPOINTS ---

app.get('/agent/summary', async (c: Context<Env>) => {
  const agents = await c.env.DB.prepare('SELECT * FROM agents ORDER BY last_seen DESC').all();
  const commands = await c.env.DB.prepare('SELECT id, description, status, result, updated_at FROM commands ORDER BY updated_at DESC LIMIT 10').all();
  
  const agentResults = agents.results as unknown as {
    name: string;
    last_seen: string;
    stats: string;
    last_screenshot: string;
  }[];
  
  const agent = agentResults[0] || null;
  // Use Unix timestamps for reliable online check
  const last_seen_unix = agent ? new Date(agent.last_seen + 'Z').getTime() : 0;
  const is_online = agent ? (Date.now() - last_seen_unix < 60000) : false;

  return c.json({
    online: is_online,
    agent: agent ? {
      name: agent.name,
      last_seen: agent.last_seen,
      stats: JSON.parse(agent.stats || '{}'),
      last_screenshot: agent.last_screenshot
    } : null,
    commands: commands.results
  });
});

app.get('/agent/assets', async (c: Context<Env>) => {
  const objects = await c.env.STORAGE.list({ limit: 20 });
  return c.json(objects.objects.map((o: any) => ({ key: o.key, uploaded: o.uploaded })));
});

app.get('/agent/asset/:key', async (c: Context<Env>) => {
  const key = c.req.param('key');
  const object = await c.env.STORAGE.get(key);
  if (!object) return c.text('Not Found', 404);
  
  const headers = new Headers();
  object.writeHttpMetadata(headers);
  headers.set('etag', object.httpEtag);
  
  return new Response(object.body, { headers });
});

app.get('/agent/logs', async (c: Context<Env>) => {
  const device_id = c.req.query('device_id');
  const logs = await c.env.DB.prepare(
    "SELECT * FROM logs WHERE device_id = ? ORDER BY created_at DESC LIMIT 50"
  ).bind(device_id).all();
  return c.json(logs.results);
});

app.post('/agent/log', async (c: Context<Env>) => {
  const data = await c.req.json();
  const { device_id, level, message } = data;
  await c.env.DB.prepare(
    "INSERT INTO logs (device_id, level, message) VALUES (?, ?, ?)"
  ).bind(device_id, level, message).run().catch(async () => {
    // Auto-create table if missing
    await c.env.DB.prepare("CREATE TABLE IF NOT EXISTS logs (device_id TEXT, level TEXT, message TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)").run();
    await c.env.DB.prepare("INSERT INTO logs (device_id, level, message) VALUES (?, ?, ?)").bind(device_id, level, message).run();
  });
  return c.json({ ok: true });
});

app.get('/brain/poll', async (c: Context<Env>) => {
  const cmds = await c.env.DB.prepare(
    "SELECT id, action, description FROM commands WHERE status = 'pending' AND description LIKE '%Priority Social Media%' LIMIT 5"
  ).all();
  
  const results = cmds.results as unknown as { id: string; action: string; description: string }[];
  
  if (results.length > 0) {
    const ids = results.map(r => r.id);
    await c.env.DB.prepare(
      `UPDATE commands SET status = 'done' WHERE id IN (${ids.map(() => '?').join(',')})`
    ).bind(...ids).run();
  }
  
  return c.json({ alerts: results.map(r => ({ alert_id: r.id, action: JSON.parse(r.action), desc: r.description })) });
});

app.post('/agent/command', async (c: Context<Env>) => {
  const data = await c.req.json();
  const { action, description, target_device } = data;
  const id = crypto.randomUUID().split('-')[0].toUpperCase();
  
  // v16 Fix: Explicitly store target_device
  await c.env.DB.prepare(
    "INSERT INTO commands (id, action, description, status, target_device, updated_at) VALUES (?, ?, ?, 'pending', ?, CURRENT_TIMESTAMP)"
  ).bind(id, JSON.stringify(action), description, target_device || null).run();
  
  return c.json({ status: 'queued', command_id: id });
});

app.get('/admin/logs', async (c: Context<Env>) => {
  const auth = c.req.header('Authorization');
  if (auth !== `Bearer ${c.env.NOIR_API_KEY}`) return c.text('Unauthorized', 401);
  
  const logs = await c.env.DB.prepare("SELECT * FROM logs ORDER BY created_at DESC LIMIT 50").all();
  return c.json(logs.results);
});

app.get('/admin/migrate', async (c: Context<Env>) => {
  try {
    await c.env.DB.prepare(`
      ALTER TABLE commands ADD COLUMN target_device TEXT;
    `).run();
  } catch(e) {}
  
  await c.env.DB.prepare(`
    ALTER TABLE agents ADD COLUMN stats TEXT;
    ALTER TABLE agents ADD COLUMN last_screenshot TEXT;
  `).run().catch(() => {});
  
  return c.text('Migration check complete. target_device column added.');
});

export default app;
