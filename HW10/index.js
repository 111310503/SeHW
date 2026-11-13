export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === "/hello") {
      return new Response("來自發布 npm 套件的問候！");
    }
    return new Response("Not Found", { status: 404 });
  }
};