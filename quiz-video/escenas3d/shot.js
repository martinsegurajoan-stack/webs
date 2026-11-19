// node shot.js pagina.html salida.jpg "expr js"  → captura de prueba
const { chromium } = require('playwright');
(async () => {
  const [, , page, out, expr] = process.argv;
  const br = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const pg = await br.newPage({ viewport: { width: 720, height: 1280 } });
  pg.on('pageerror', e => console.error('ERR', e.message));
  await pg.goto(`http://127.0.0.1:8765/escenas3d/${page}`);
  await pg.waitForFunction(() => window.ok === true, null, { timeout: 60000 });
  const exprs = expr.split(';;');
  for (let i = 0; i < exprs.length; i++) {
    await pg.evaluate(exprs[i]);
    await pg.screenshot({ path: out.replace('.jpg', `_${i}.jpg`), type: 'jpeg', quality: 92 });
  }
  await br.close();
})();
