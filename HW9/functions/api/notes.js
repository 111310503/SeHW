let memoryStore = [
  { id: '1', text: '歡迎來到 Cloudflare Pages！', createdAt: Date.now() }
];

export async function onRequestGet(context) {
  const { env } = context;

  if (env.NOTES_KV) {
    const rawData = await env.NOTES_KV.get('user_notes');
    const notes = rawData ? JSON.parse(rawData) : [];
    return Response.json(notes);
  }

  return Response.json(memoryStore);
}

export async function onRequestPost(context) {
  const { request, env } = context;

  try {
    const body = await request.json();
    if (!body || !body.text) {
      return new Response(JSON.stringify({ error: 'Text is required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const newNote = {
      id: crypto.randomUUID(),
      text: body.text.slice(0, 100),
      createdAt: Date.now()
    };

    if (env.NOTES_KV) {
      const rawData = await env.NOTES_KV.get('user_notes');
      const notes = rawData ? JSON.parse(rawData) : [];
      notes.unshift(newNote);
      await env.NOTES_KV.put('user_notes', JSON.stringify(notes.slice(0, 50)));
      return Response.json(newNote, { status: 201 });
    }

    memoryStore.unshift(newNote);
    memoryStore = memoryStore.slice(0, 50);
    return Response.json(newNote, { status: 201 });
  } catch (err) {
    return new Response(JSON.stringify({ error: 'Invalid JSON' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}