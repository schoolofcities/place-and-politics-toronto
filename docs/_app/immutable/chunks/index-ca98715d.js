function C(){}function ut(t,e){for(const n in e)t[n]=e[n];return t}function X(t){return t()}function U(){return Object.create(null)}function v(t){t.forEach(X)}function Y(t){return typeof t=="function"}function Mt(t,e){return t!=t?e==e:t!==e||t&&typeof t=="object"||typeof t=="function"}let T;function Ct(t,e){return T||(T=document.createElement("a")),T.href=e,t===T.href}function at(t){return Object.keys(t).length===0}function ft(t,...e){if(t==null)return C;const n=t.subscribe(...e);return n.unsubscribe?()=>n.unsubscribe():n}function jt(t,e,n){t.$$.on_destroy.push(ft(e,n))}function Ht(t,e,n,i){if(t){const s=Z(t,e,n,i);return t[0](s)}}function Z(t,e,n,i){return t[1]&&i?ut(n.ctx.slice(),t[1](i(e))):n.ctx}function Dt(t,e,n,i){if(t[2]&&i){const s=t[2](i(n));if(e.dirty===void 0)return s;if(typeof s=="object"){const o=[],r=Math.max(e.dirty.length,s.length);for(let l=0;l<r;l+=1)o[l]=e.dirty[l]|s[l];return o}return e.dirty|s}return e.dirty}function Lt(t,e,n,i,s,o){if(s){const r=Z(e,n,i,o);t.p(r,s)}}function zt(t){if(t.ctx.length>32){const e=[],n=t.ctx.length/32;for(let i=0;i<n;i++)e[i]=-1;return e}return-1}function Ot(t,e,n){return t.set(n),e}let j=!1;function dt(){j=!0}function _t(){j=!1}function ht(t,e,n,i){for(;t<e;){const s=t+(e-t>>1);n(s)<=i?t=s+1:e=s}return t}function mt(t){if(t.hydrate_init)return;t.hydrate_init=!0;let e=t.childNodes;if(t.nodeName==="HEAD"){const c=[];for(let u=0;u<e.length;u++){const f=e[u];f.claim_order!==void 0&&c.push(f)}e=c}const n=new Int32Array(e.length+1),i=new Int32Array(e.length);n[0]=-1;let s=0;for(let c=0;c<e.length;c++){const u=e[c].claim_order,f=(s>0&&e[n[s]].claim_order<=u?s+1:ht(1,s,d=>e[n[d]].claim_order,u))-1;i[c]=n[f]+1;const _=f+1;n[_]=c,s=Math.max(_,s)}const o=[],r=[];let l=e.length-1;for(let c=n[s]+1;c!=0;c=i[c-1]){for(o.push(e[c-1]);l>=c;l--)r.push(e[l]);l--}for(;l>=0;l--)r.push(e[l]);o.reverse(),r.sort((c,u)=>c.claim_order-u.claim_order);for(let c=0,u=0;c<r.length;c++){for(;u<o.length&&r[c].claim_order>=o[u].claim_order;)u++;const f=u<o.length?o[u]:null;t.insertBefore(r[c],f)}}function pt(t,e){t.appendChild(e)}function yt(t,e){if(j){for(mt(t),(t.actual_end_child===void 0||t.actual_end_child!==null&&t.actual_end_child.parentNode!==t)&&(t.actual_end_child=t.firstChild);t.actual_end_child!==null&&t.actual_end_child.claim_order===void 0;)t.actual_end_child=t.actual_end_child.nextSibling;e!==t.actual_end_child?(e.claim_order!==void 0||e.parentNode!==t)&&t.insertBefore(e,t.actual_end_child):t.actual_end_child=e.nextSibling}else(e.parentNode!==t||e.nextSibling!==null)&&t.appendChild(e)}function gt(t,e,n){t.insertBefore(e,n||null)}function wt(t,e,n){j&&!n?yt(t,e):(e.parentNode!==t||e.nextSibling!=n)&&t.insertBefore(e,n||null)}function x(t){t.parentNode.removeChild(t)}function Pt(t,e){for(let n=0;n<t.length;n+=1)t[n]&&t[n].d(e)}function G(t){return document.createElement(t)}function tt(t){return document.createElementNS("http://www.w3.org/2000/svg",t)}function R(t){return document.createTextNode(t)}function Bt(){return R(" ")}function Wt(){return R("")}function J(t,e,n,i){return t.addEventListener(e,n,i),()=>t.removeEventListener(e,n,i)}function qt(t){return function(e){return e.preventDefault(),t.call(this,e)}}function et(t,e,n){n==null?t.removeAttribute(e):t.getAttribute(e)!==n&&t.setAttribute(e,n)}function Gt(t,e){const n=Object.getOwnPropertyDescriptors(t.__proto__);for(const i in e)e[i]==null?t.removeAttribute(i):i==="style"?t.style.cssText=e[i]:i==="__value"?t.value=t[i]=e[i]:n[i]&&n[i].set?t[i]=e[i]:et(t,i,e[i])}function Rt(t,e,n){e in t?t[e]=typeof t[e]=="boolean"&&n===""?!0:n:et(t,e,n)}function bt(t){return Array.from(t.childNodes)}function nt(t){t.claim_info===void 0&&(t.claim_info={last_index:0,total_claimed:0})}function it(t,e,n,i,s=!1){nt(t);const o=(()=>{for(let r=t.claim_info.last_index;r<t.length;r++){const l=t[r];if(e(l)){const c=n(l);return c===void 0?t.splice(r,1):t[r]=c,s||(t.claim_info.last_index=r),l}}for(let r=t.claim_info.last_index-1;r>=0;r--){const l=t[r];if(e(l)){const c=n(l);return c===void 0?t.splice(r,1):t[r]=c,s?c===void 0&&t.claim_info.last_index--:t.claim_info.last_index=r,l}}return i()})();return o.claim_order=t.claim_info.total_claimed,t.claim_info.total_claimed+=1,o}function st(t,e,n,i){return it(t,s=>s.nodeName===e,s=>{const o=[];for(let r=0;r<s.attributes.length;r++){const l=s.attributes[r];n[l.name]||o.push(l.name)}o.forEach(r=>s.removeAttribute(r))},()=>i(e))}function Ft(t,e,n){return st(t,e,n,G)}function It(t,e,n){return st(t,e,n,tt)}function xt(t,e){return it(t,n=>n.nodeType===3,n=>{const i=""+e;if(n.data.startsWith(i)){if(n.data.length!==i.length)return n.splitText(i.length)}else n.data=i},()=>R(e),!0)}function Ut(t){return xt(t," ")}function K(t,e,n){for(let i=n;i<t.length;i+=1){const s=t[i];if(s.nodeType===8&&s.textContent.trim()===e)return i}return t.length}function Jt(t,e){const n=K(t,"HTML_TAG_START",0),i=K(t,"HTML_TAG_END",n);if(n===i)return new Q(void 0,e);nt(t);const s=t.splice(n,i-n+1);x(s[0]),x(s[s.length-1]);const o=s.slice(1,s.length-1);for(const r of o)r.claim_order=t.claim_info.total_claimed,t.claim_info.total_claimed+=1;return new Q(o,e)}function Kt(t,e){e=""+e,t.wholeText!==e&&(t.data=e)}function Qt(t,e){t.value=e==null?"":e}function Vt(t,e,n,i){n===null?t.style.removeProperty(e):t.style.setProperty(e,n,i?"important":"")}let k;function $t(){if(k===void 0){k=!1;try{typeof window<"u"&&window.parent&&window.parent.document}catch{k=!0}}return k}function Xt(t,e){getComputedStyle(t).position==="static"&&(t.style.position="relative");const i=G("iframe");i.setAttribute("style","display: block; position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; border: 0; opacity: 0; pointer-events: none; z-index: -1;"),i.setAttribute("aria-hidden","true"),i.tabIndex=-1;const s=$t();let o;return s?(i.src="data:text/html,<script>onresize=function(){parent.postMessage(0,'*')}<\/script>",o=J(window,"message",r=>{r.source===i.contentWindow&&e()})):(i.src="about:blank",i.onload=()=>{o=J(i.contentWindow,"resize",e)}),pt(t,i),()=>{(s||o&&i.contentWindow)&&o(),x(i)}}function Yt(t,e,n){t.classList[n?"add":"remove"](e)}function vt(t,e,{bubbles:n=!1,cancelable:i=!1}={}){const s=document.createEvent("CustomEvent");return s.initCustomEvent(t,n,i,e),s}function Zt(t,e){const n=[];let i=0;for(const s of e.childNodes)if(s.nodeType===8){const o=s.textContent.trim();o===`HEAD_${t}_END`?(i-=1,n.push(s)):o===`HEAD_${t}_START`&&(i+=1,n.push(s))}else i>0&&n.push(s);return n}class Et{constructor(e=!1){this.is_svg=!1,this.is_svg=e,this.e=this.n=null}c(e){this.h(e)}m(e,n,i=null){this.e||(this.is_svg?this.e=tt(n.nodeName):this.e=G(n.nodeName),this.t=n,this.c(e)),this.i(i)}h(e){this.e.innerHTML=e,this.n=Array.from(this.e.childNodes)}i(e){for(let n=0;n<this.n.length;n+=1)gt(this.t,this.n[n],e)}p(e){this.d(),this.h(e),this.i(this.a)}d(){this.n.forEach(x)}}class Q extends Et{constructor(e,n=!1){super(n),this.e=this.n=null,this.l=e}c(e){this.l?this.n=this.l:super.c(e)}i(e){for(let n=0;n<this.n.length;n+=1)wt(this.t,this.n[n],e)}}function te(t,e){return new t(e)}let $;function b(t){$=t}function H(){if(!$)throw new Error("Function called outside component initialization");return $}function ee(t){H().$$.before_update.push(t)}function ne(t){H().$$.on_mount.push(t)}function ie(t){H().$$.after_update.push(t)}function se(){const t=H();return(e,n,{cancelable:i=!1}={})=>{const s=t.$$.callbacks[e];if(s){const o=vt(e,n,{cancelable:i});return s.slice().forEach(r=>{r.call(t,o)}),!o.defaultPrevented}return!0}}const w=[],V=[],S=[],B=[],rt=Promise.resolve();let W=!1;function ct(){W||(W=!0,rt.then(ot))}function re(){return ct(),rt}function q(t){S.push(t)}function ce(t){B.push(t)}const P=new Set;let N=0;function ot(){const t=$;do{for(;N<w.length;){const e=w[N];N++,b(e),At(e.$$)}for(b(null),w.length=0,N=0;V.length;)V.pop()();for(let e=0;e<S.length;e+=1){const n=S[e];P.has(n)||(P.add(n),n())}S.length=0}while(w.length);for(;B.length;)B.pop()();W=!1,P.clear(),b(t)}function At(t){if(t.fragment!==null){t.update(),v(t.before_update);const e=t.dirty;t.dirty=[-1],t.fragment&&t.fragment.p(t.ctx,e),t.after_update.forEach(q)}}const M=new Set;let g;function oe(){g={r:0,c:[],p:g}}function le(){g.r||v(g.c),g=g.p}function lt(t,e){t&&t.i&&(M.delete(t),t.i(e))}function Tt(t,e,n,i){if(t&&t.o){if(M.has(t))return;M.add(t),g.c.push(()=>{M.delete(t),i&&(n&&t.d(1),i())}),t.o(e)}else i&&i()}function ue(t,e){Tt(t,1,1,()=>{e.delete(t.key)})}function ae(t,e,n,i,s,o,r,l,c,u,f,_){let d=t.length,m=o.length,h=d;const D={};for(;h--;)D[t[h].key]=h;const E=[],L=new Map,z=new Map;for(h=m;h--;){const a=_(s,o,h),p=n(a);let y=r.get(p);y?i&&y.p(a,e):(y=u(p,a),y.c()),L.set(p,E[h]=y),p in D&&z.set(p,Math.abs(h-D[p]))}const F=new Set,I=new Set;function O(a){lt(a,1),a.m(l,f),r.set(a.key,a),f=a.first,m--}for(;d&&m;){const a=E[m-1],p=t[d-1],y=a.key,A=p.key;a===p?(f=a.first,d--,m--):L.has(A)?!r.has(y)||F.has(y)?O(a):I.has(A)?d--:z.get(y)>z.get(A)?(I.add(y),O(a)):(F.add(A),d--):(c(p,r),d--)}for(;d--;){const a=t[d];L.has(a.key)||c(a,r)}for(;m;)O(E[m-1]);return E}function fe(t,e){const n={},i={},s={$$scope:1};let o=t.length;for(;o--;){const r=t[o],l=e[o];if(l){for(const c in r)c in l||(i[c]=1);for(const c in l)s[c]||(n[c]=l[c],s[c]=1);t[o]=l}else for(const c in r)s[c]=1}for(const r in i)r in n||(n[r]=void 0);return n}function de(t){return typeof t=="object"&&t!==null?t:{}}function _e(t,e,n){const i=t.$$.props[e];i!==void 0&&(t.$$.bound[i]=n,n(t.$$.ctx[i]))}function he(t){t&&t.c()}function me(t,e){t&&t.l(e)}function kt(t,e,n,i){const{fragment:s,after_update:o}=t.$$;s&&s.m(e,n),i||q(()=>{const r=t.$$.on_mount.map(X).filter(Y);t.$$.on_destroy?t.$$.on_destroy.push(...r):v(r),t.$$.on_mount=[]}),o.forEach(q)}function Nt(t,e){const n=t.$$;n.fragment!==null&&(v(n.on_destroy),n.fragment&&n.fragment.d(e),n.on_destroy=n.fragment=null,n.ctx=[])}function St(t,e){t.$$.dirty[0]===-1&&(w.push(t),ct(),t.$$.dirty.fill(0)),t.$$.dirty[e/31|0]|=1<<e%31}function pe(t,e,n,i,s,o,r,l=[-1]){const c=$;b(t);const u=t.$$={fragment:null,ctx:[],props:o,update:C,not_equal:s,bound:U(),on_mount:[],on_destroy:[],on_disconnect:[],before_update:[],after_update:[],context:new Map(e.context||(c?c.$$.context:[])),callbacks:U(),dirty:l,skip_bound:!1,root:e.target||c.$$.root};r&&r(u.root);let f=!1;if(u.ctx=n?n(t,e.props||{},(_,d,...m)=>{const h=m.length?m[0]:d;return u.ctx&&s(u.ctx[_],u.ctx[_]=h)&&(!u.skip_bound&&u.bound[_]&&u.bound[_](h),f&&St(t,_)),d}):[],u.update(),f=!0,v(u.before_update),u.fragment=i?i(u.ctx):!1,e.target){if(e.hydrate){dt();const _=bt(e.target);u.fragment&&u.fragment.l(_),_.forEach(x)}else u.fragment&&u.fragment.c();e.intro&&lt(t.$$.fragment),kt(t,e.target,e.anchor,e.customElement),_t(),ot()}b(c)}class ye{$destroy(){Nt(this,1),this.$destroy=C}$on(e,n){if(!Y(n))return C;const i=this.$$.callbacks[e]||(this.$$.callbacks[e]=[]);return i.push(n),()=>{const s=i.indexOf(n);s!==-1&&i.splice(s,1)}}$set(e){this.$$set&&!at(e)&&(this.$$.skip_bound=!0,this.$$set(e),this.$$.skip_bound=!1)}}export{ut as $,re as A,C as B,Ht as C,Lt as D,zt as E,Dt as F,yt as G,jt as H,Zt as I,q as J,Xt as K,Ct as L,tt as M,It as N,Pt as O,J as P,Y as Q,Ot as R,ye as S,Yt as T,v as U,se as V,ee as W,V as X,Rt as Y,ae as Z,ue as _,Bt as a,Gt as a0,Qt as a1,fe as a2,de as a3,qt as a4,_e as a5,ce as a6,Q as a7,Jt as a8,wt as b,Ut as c,le as d,Wt as e,lt as f,oe as g,x as h,pe as i,ie as j,G as k,Ft as l,bt as m,et as n,ne as o,Vt as p,R as q,xt as r,Mt as s,Tt as t,Kt as u,te as v,he as w,me as x,kt as y,Nt as z};