import{S as _e,i as ye,s as ge,k as me,M as g,q,e as X,l as pe,m as f,N as m,r as F,h as n,n as t,p,J as ve,b as Z,G as c,K as be,u as H,B as he,O as $}from"./index-ca98715d.js";import{t as we,g as ke,a as Ee}from"./transform-9a8d1a54.js";import{W as Y}from"./wards.geo-c8a78e6c.js";function oe(a,s,r){const i=a.slice();return i[12]=s[r],i}function ce(a,s,r){const i=a.slice();return i[12]=s[r],i}function ne(a,s,r){const i=a.slice();return i[12]=s[r],i}function ue(a){let s,r,i;return{c(){s=g("path"),this.h()},l(h){s=m(h,"path",{class:!0,d:!0,fill:!0}),f(s).forEach(n),this.h()},h(){t(s,"class","ct svelte-8dhls0"),t(s,"d",r=a[4](a[12])),t(s,"fill",i=a[12].properties["color_"+a[0]])},m(h,v){Z(h,s,v)},p(h,v){v&16&&r!==(r=h[4](h[12]))&&t(s,"d",r),v&1&&i!==(i=h[12].properties["color_"+h[0]])&&t(s,"fill",i)},d(h){h&&n(s)}}}function fe(a){let s,r;return{c(){s=g("path"),this.h()},l(i){s=m(i,"path",{class:!0,d:!0}),f(s).forEach(n),this.h()},h(){t(s,"class","wardwhite svelte-8dhls0"),t(s,"d",r=a[4](a[12]))},m(i,h){Z(i,s,h)},p(i,h){h&16&&r!==(r=i[4](i[12]))&&t(s,"d",r)},d(i){i&&n(s)}}}function de(a){let s,r;return{c(){s=g("path"),this.h()},l(i){s=m(i,"path",{class:!0,d:!0}),f(s).forEach(n),this.h()},h(){t(s,"class","ward svelte-8dhls0"),t(s,"d",r=a[4](a[12]))},m(i,h){Z(i,s,h)},p(i,h){h&16&&r!==(r=i[4](i[12]))&&t(s,"d",r)},d(i){i&&n(s)}}}function Me(a){let s,r,i,h=a[6][a[0]].name+" "+a[6][a[0]].year+" ("+a[6][a[0]].citywide+" of the vote citywide)",v,P,w,b,S,T,G,W,j=a[6][a[0]].breaks[3]*100+"%",K,u,R=a[6][a[0]].breaks[2]*100+"%",L,O,V=a[6][a[0]].breaks[1]*100+"%",Q,z,A=a[6][a[0]].breaks[0]*100+"%",U,k,E,M,x,J,ee,B=a[7],d=[];for(let l=0;l<B.length;l+=1)d[l]=ue(ne(a,B,l));let I=Y.features,_=[];for(let l=0;l<I.length;l+=1)_[l]=fe(ce(a,I,l));let N=Y.features,y=[];for(let l=0;l<N.length;l+=1)y[l]=de(oe(a,N,l));return{c(){s=me("div"),r=g("svg"),i=g("text"),v=q(h);for(let l=0;l<d.length;l+=1)d[l].c();P=X();for(let l=0;l<_.length;l+=1)_[l].c();w=X();for(let l=0;l<y.length;l+=1)y[l].c();b=g("text"),S=q("% of"),T=g("text"),G=q("vote"),W=g("text"),K=q(j),u=g("text"),L=q(R),O=g("text"),Q=q(V),z=g("text"),U=q(A),k=g("rect"),E=g("rect"),M=g("rect"),x=g("rect"),J=g("rect"),this.h()},l(l){s=pe(l,"DIV",{});var o=f(s);r=m(o,"svg",{width:!0,height:!0,id:!0,class:!0});var e=f(r);i=m(e,"text",{class:!0,x:!0,y:!0});var C=f(i);v=F(C,h),C.forEach(n);for(let D=0;D<d.length;D+=1)d[D].l(e);P=X();for(let D=0;D<_.length;D+=1)_[D].l(e);w=X();for(let D=0;D<y.length;D+=1)y[D].l(e);b=m(e,"text",{class:!0,x:!0,y:!0});var te=f(b);S=F(te,"% of"),te.forEach(n),T=m(e,"text",{class:!0,x:!0,y:!0});var le=f(T);G=F(le,"vote"),le.forEach(n),W=m(e,"text",{class:!0,x:!0,y:!0});var re=f(W);K=F(re,j),re.forEach(n),u=m(e,"text",{class:!0,x:!0,y:!0});var ae=f(u);L=F(ae,R),ae.forEach(n),O=m(e,"text",{class:!0,x:!0,y:!0});var se=f(O);Q=F(se,V),se.forEach(n),z=m(e,"text",{class:!0,x:!0,y:!0});var ie=f(z);U=F(ie,A),ie.forEach(n),k=m(e,"rect",{class:!0,width:!0,height:!0,x:!0,y:!0,style:!0}),f(k).forEach(n),E=m(e,"rect",{class:!0,width:!0,height:!0,x:!0,y:!0,style:!0}),f(E).forEach(n),M=m(e,"rect",{class:!0,width:!0,height:!0,x:!0,y:!0,style:!0}),f(M).forEach(n),x=m(e,"rect",{class:!0,width:!0,height:!0,x:!0,y:!0,style:!0}),f(x).forEach(n),J=m(e,"rect",{class:!0,width:!0,height:!0,x:!0,y:!0,style:!0}),f(J).forEach(n),e.forEach(n),o.forEach(n),this.h()},h(){t(i,"class","label svelte-8dhls0"),t(i,"x","12"),t(i,"y","22"),t(b,"class","label svelte-8dhls0"),t(b,"x","320"),t(b,"y","185"),t(T,"class","label svelte-8dhls0"),t(T,"x","320"),t(T,"y","200"),t(W,"class","label svelte-8dhls0"),t(W,"x","373"),t(W,"y","170"),t(u,"class","label svelte-8dhls0"),t(u,"x","373"),t(u,"y","185"),t(O,"class","label svelte-8dhls0"),t(O,"x","373"),t(O,"y","200"),t(z,"class","label svelte-8dhls0"),t(z,"x","373"),t(z,"y","215"),t(k,"class","box"),t(k,"width","20"),t(k,"height","15"),t(k,"x","350"),t(k,"y","150"),p(k,"fill",a[1][4]),p(k,"stroke","white"),t(E,"class","box"),t(E,"width","20"),t(E,"height","15"),t(E,"x","350"),t(E,"y","165"),p(E,"fill",a[1][3]),p(E,"stroke","white"),t(M,"class","box"),t(M,"width","20"),t(M,"height","15"),t(M,"x","350"),t(M,"y","180"),p(M,"fill",a[1][2]),p(M,"stroke","white"),t(x,"class","box"),t(x,"width","20"),t(x,"height","15"),t(x,"x","350"),t(x,"y","195"),p(x,"fill",a[1][1]),p(x,"stroke","white"),t(J,"class","box"),t(J,"width","20"),t(J,"height","15"),t(J,"x","350"),t(J,"y","210"),p(J,"fill",a[1][0]),p(J,"stroke","white"),t(r,"width",a[3]),t(r,"height",a[5]),t(r,"id",a[0]),t(r,"class","svelte-8dhls0"),ve(()=>a[10].call(s))},m(l,o){Z(l,s,o),c(s,r),c(r,i),c(i,v);for(let e=0;e<d.length;e+=1)d[e].m(r,null);c(r,P);for(let e=0;e<_.length;e+=1)_[e].m(r,null);c(r,w);for(let e=0;e<y.length;e+=1)y[e].m(r,null);c(r,b),c(b,S),c(r,T),c(T,G),c(r,W),c(W,K),c(r,u),c(u,L),c(r,O),c(O,Q),c(r,z),c(z,U),c(r,k),c(r,E),c(r,M),c(r,x),c(r,J),ee=be(s,a[10].bind(s))},p(l,[o]){if(o&1&&h!==(h=l[6][l[0]].name+" "+l[6][l[0]].year+" ("+l[6][l[0]].citywide+" of the vote citywide)")&&H(v,h),o&145){B=l[7];let e;for(e=0;e<B.length;e+=1){const C=ne(l,B,e);d[e]?d[e].p(C,o):(d[e]=ue(C),d[e].c(),d[e].m(r,P))}for(;e<d.length;e+=1)d[e].d(1);d.length=B.length}if(o&16){I=Y.features;let e;for(e=0;e<I.length;e+=1){const C=ce(l,I,e);_[e]?_[e].p(C,o):(_[e]=fe(C),_[e].c(),_[e].m(r,w))}for(;e<_.length;e+=1)_[e].d(1);_.length=I.length}if(o&16){N=Y.features;let e;for(e=0;e<N.length;e+=1){const C=oe(l,N,e);y[e]?y[e].p(C,o):(y[e]=de(C),y[e].c(),y[e].m(r,b))}for(;e<y.length;e+=1)y[e].d(1);y.length=N.length}o&1&&j!==(j=l[6][l[0]].breaks[3]*100+"%")&&H(K,j),o&1&&R!==(R=l[6][l[0]].breaks[2]*100+"%")&&H(L,R),o&1&&V!==(V=l[6][l[0]].breaks[1]*100+"%")&&H(Q,V),o&1&&A!==(A=l[6][l[0]].breaks[0]*100+"%")&&H(U,A),o&2&&p(k,"fill",l[1][4]),o&2&&p(E,"fill",l[1][3]),o&2&&p(M,"fill",l[1][2]),o&2&&p(x,"fill",l[1][1]),o&2&&p(J,"fill",l[1][0]),o&8&&t(r,"width",l[3]),o&32&&t(r,"height",l[5]),o&1&&t(r,"id",l[0])},i:he,o:he,d(l){l&&n(s),$(d,l),$(_,l),$(y,l),ee()}}}function xe(a,s,r){let i,h,v,P,{candidate:w}=s,{tracts:b}=s,{colours:S}=s;const T={pcttory_john2022:{breaks:[.4,.5,.6,.7],name:"John Tory",year:"2022",citywide:"62%"},pcttory2018:{breaks:[.4,.5,.6,.7],name:"John Tory",year:"2018",citywide:"63%"},pcttory2014:{breaks:[.2,.3,.4,.5],name:"John Tory",year:"2014",citywide:"40%"},pcttory2003:{breaks:[.2,.3,.4,.5],name:"John Tory",year:"2003",citywide:"38%"},pctpitfield2006:{breaks:[.2,.3,.4,.5],name:"Jane Pitfield",year:"2006",citywide:"32%"},pctford2010:{breaks:[.3,.4,.5,.6],name:"Rob Ford",year:"2010",citywide:"47%"},pctford2014:{breaks:[.3,.4,.5,.6],name:"Doug Ford",year:"2014",citywide:"34%"},pctgomberg2000:{breaks:[.1,.2,.3,.4],name:"Tooker Gomberg",year:"2000",citywide:"8%"},pctchow2014:{breaks:[.1,.2,.3,.4],name:"Olivia Chow",year:"2014",citywide:"23%"},pctkeesmaat2018:{breaks:[.1,.2,.3,.4],name:"Jennifer Keesmaat",year:"2018",citywide:"23%"},pctpenalosa_gil2022:{breaks:[.1,.2,.3,.4],name:"Gil Pe\xF1alosa",year:"2022",citywide:"18%"},pctmiller2003:{breaks:[.3,.4,.5,.6],name:"David Miller",year:"2003",citywide:"43%"},pctmiller2006:{breaks:[.3,.4,.5,.6],name:"David Miller",year:"2006",citywide:"57%"},pctsmitherman2010:{breaks:[.3,.4,.5,.6],name:"George Smitherman",year:"2010",citywide:"36%"},pctchow_olivia2023:{breaks:[.1,.2,.3,.4],name:"Olivia Chow",year:"2023",citywide:"37%"},chow_ch2014_2023:{breaks:[0,.1,.2,.3],name:"Olivia Chow",year:"2014 to 2023",citywide:"14% increase"}};let G=420,W=b.features;var j=we().domain(T[w].breaks).range(S);W.map(u=>{u.properties[w]?u.properties["color_"+w]=j(u.properties[w]):u.properties["color_"+w]="white"});function K(){G=this.offsetWidth,r(2,G)}return a.$$set=u=>{"candidate"in u&&r(0,w=u.candidate),"tracts"in u&&r(8,b=u.tracts),"colours"in u&&r(1,S=u.colours)},a.$$.update=()=>{a.$$.dirty&4&&r(3,i=G),a.$$.dirty&8&&r(5,h=i/1.75),a.$$.dirty&8&&r(9,v=ke().center([-78.155-.00239*i+1125e-9*i**2,43.54+45e-5*i-25e-8*i**2]).scale([82e3*i/800]).angle([-17])),a.$$.dirty&512&&r(4,P=Ee(v))},[w,S,G,i,P,h,T,W,b,v,K]}class Ce extends _e{constructor(s){super(),ye(this,s,xe,Me,ge,{candidate:0,tracts:8,colours:1})}}export{Ce as M};