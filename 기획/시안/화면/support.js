/* 오프라인 보기용 런타임.
 * claude.ai 캔버스 없이 *.dc.html 시안을 브라우저에서 바로 열 수 있게 한다.
 * 지원: {{a.b}} 끼우기, <sc-for list as>, <sc-if value>, onClick·onMouseEnter·onChange,
 *       DCLogic(state·setState·props), componentDidMount·componentWillUnmount, <dc-import>.
 * 그림·글꼴은 같은 폴더의 _blob/ 에서 읽는다(원래 주소 /_blob/… 를 바꿔 읽음). */
(function () {
  'use strict';
  function fixUrl(s) { return typeof s === 'string' ? s.replace(/\/_blob\//g, '_blob/') : s; }

  class DCLogic {
    constructor(props) { this.props = props || {}; this.state = {}; }
    setState(patch) {
      const p = typeof patch === 'function' ? patch(this.state, this.props) : patch;
      this.state = Object.assign({}, this.state, p);
      scheduleRender();
    }
  }
  window.DCLogic = DCLogic;

  let comp = null, template = null, root = null, pending = false, mounted = false;

  function scheduleRender() {
    if (pending) return;
    pending = true;
    requestAnimationFrame(function () { pending = false; render(); });
  }

  function lookup(scope, expr) {
    expr = expr.trim();
    if (expr === 'true') return true;
    if (expr === 'false') return false;
    if (expr === 'null') return null;
    if (/^-?\d+(\.\d+)?$/.test(expr)) return Number(expr);
    if (/^'.*'$|^".*"$/.test(expr)) return expr.slice(1, -1);
    const parts = expr.split('.');
    let s = scope;
    while (s && !(parts[0] in s.vars)) s = s.parent;
    if (!s) return undefined;
    let v = s.vars[parts[0]];
    for (let i = 1; i < parts.length; i++) { if (v == null) return undefined; v = v[parts[i]]; }
    return v;
  }
  const WHOLE = /^\s*\{\{([^}]*)\}\}\s*$/;
  function interp(scope, str) {
    return str.replace(/\{\{([^}]*)\}\}/g, function (_, e) {
      const v = lookup(scope, e);
      return v == null ? '' : String(v);
    });
  }

  const EVENTS = { onclick: 'click', onmouseenter: 'mouseenter', onmouseleave: 'mouseleave', onchange: 'change', oninput: 'input' };
  const BOOL_ATTRS = { checked: 1, disabled: 1, selected: 1, hidden: 1, readonly: 1 };

  function renderNodes(nodes, scope, out) {
    nodes.forEach(function (n) { renderNode(n, scope, out); });
  }

  function renderNode(node, scope, out) {
    if (node.nodeType === 3) { out.appendChild(document.createTextNode(interp(scope, node.nodeValue))); return; }
    if (node.nodeType !== 1) return;
    const tag = node.tagName.toLowerCase();
    if (tag === 'helmet') return;
    if (tag === 'sc-for') {
      const list = lookup(scope, (node.getAttribute('list') || '').replace(/^\{\{|\}\}$/g, '')) || [];
      const as = node.getAttribute('as') || 'item';
      list.forEach(function (item, i) {
        const vars = {}; vars[as] = item; vars[as + 'Index'] = i;
        renderNodes(Array.from(node.childNodes), { vars: vars, parent: scope }, out);
      });
      return;
    }
    if (tag === 'sc-if') {
      const v = lookup(scope, (node.getAttribute('value') || '').replace(/^\{\{|\}\}$/g, ''));
      if (v) renderNodes(Array.from(node.childNodes), scope, out);
      return;
    }
    if (tag === 'dc-import') {
      const name = node.getAttribute('name');
      const size = (node.getAttribute('hint-size') || '390px,844px').split(',');
      const params = new URLSearchParams();
      Array.from(node.attributes).forEach(function (a) {
        if (a.name === 'name' || a.name.indexOf('hint-') === 0) return;
        const key = a.name.replace(/-([a-z])/g, function (_, c) { return c.toUpperCase(); });
        params.set(key, interp(scope, a.value));
      });
      const f = document.createElement('iframe');
      f.src = name + '.dc.html?' + params.toString();
      f.style.cssText = 'border:0;display:block;width:' + size[0].trim() + ';height:' + size[1].trim();
      out.appendChild(f);
      return;
    }
    const ns = node.namespaceURI;
    const el = (ns && ns !== 'http://www.w3.org/1999/xhtml') ? document.createElementNS(ns, node.localName) : document.createElement(node.localName);
    Array.from(node.attributes).forEach(function (a) {
      const name = a.name, lname = name.toLowerCase();
      if (lname.indexOf('hint-') === 0) return;
      const whole = a.value.match(WHOLE);
      if (EVENTS[lname]) {
        const fn = whole ? lookup(scope, whole[1]) : null;
        if (typeof fn === 'function') {
          el.addEventListener(EVENTS[lname], fn);
          if (lname === 'onchange' && (tag === 'input' || tag === 'textarea')) {
            /* 글자 입력 중 화면을 다시 그리면 커서가 사라지므로 칸을 벗어날 때 반영한다 */
          }
        }
        return;
      }
      if (whole && BOOL_ATTRS[lname]) {
        const v = lookup(scope, whole[1]);
        if (v) el.setAttribute(name, '');
        if (lname === 'checked') el.checked = !!v;
        return;
      }
      let val = interp(scope, a.value);
      if (lname === 'src' || lname === 'href' || lname === 'style') val = fixUrl(val);
      el.setAttribute(name, val);
      if (lname === 'value' && (tag === 'input' || tag === 'textarea')) el.value = val;
    });
    renderNodes(Array.from(node.childNodes), scope, tag === 'template' ? el.content : el);
    out.appendChild(el);
  }

  function render() {
    if (!comp) return;
    let vals;
    try { vals = comp.renderVals ? comp.renderVals() : {}; }
    catch (e) { console.error(e); return; }
    const frag = document.createDocumentFragment();
    renderNodes(Array.from(template.childNodes), { vars: vals || {}, parent: null }, frag);
    root.replaceChildren(frag);
    if (!mounted) { mounted = true; if (comp.componentDidMount) comp.componentDidMount(); }
  }

  function start() {
    root = document.querySelector('x-dc');
    if (!root) return;
    template = root.cloneNode(true);
    const helmet = template.querySelector('helmet');
    if (helmet) {
      Array.from(helmet.children).forEach(function (c) {
        const n = c.cloneNode(true);
        if (n.tagName === 'STYLE') n.textContent = fixUrl(n.textContent);
        document.head.appendChild(n);
      });
    }
    const sc = document.querySelector('script[data-dc-script]');
    let props = {};
    if (sc) {
      try { props = JSON.parse(sc.getAttribute('data-props') || '{}'); } catch (e) { props = {}; }
      const preview = props.$preview; delete props.$preview;
      Object.keys(props).forEach(function (k) {
        const v = props[k];
        if (v && typeof v === 'object' && 'editor' in v) props[k] = undefined;
      });
      new URLSearchParams(location.search).forEach(function (v, k) { props[k] = v; });
      if (preview && !window.frameElement) {
        document.body.style.margin = '0';
      }
      let Comp = null;
      try { Comp = new Function('DCLogic', sc.textContent + '\nreturn typeof Component !== "undefined" ? Component : null;')(DCLogic); }
      catch (e) { console.error('시안 스크립트 오류', e); }
      comp = Comp ? new Comp(props) : new DCLogic(props);
      if (!comp.state) comp.state = {};
    } else {
      comp = new DCLogic({});
    }
    window.addEventListener('beforeunload', function () { if (comp && comp.componentWillUnmount) comp.componentWillUnmount(); });
    render();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
