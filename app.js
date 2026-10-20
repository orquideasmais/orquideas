(function(){var $=function(s,r){return(r||document).querySelector(s)},$$=function(s,r){return[].slice.call((r||document).querySelectorAll(s))};
var q=$("#q"),cat="Todas";function filt(){var t=q?q.value.toLowerCase():"";$$(".card").forEach(function(c){var ok=(cat=="Todas"||c.dataset.c==cat)&&c.dataset.t.indexOf(t)>-1;c.style.display=ok?"":"none"})}
if(q)q.oninput=filt;$$(".chip").forEach(function(b){b.onclick=function(){cat=b.dataset.c;$$(".chip").forEach(function(x){x.classList.toggle("on",x==b)});filt()}});
var g=$("#gq");if(g)g.oninput=function(){var t=g.value.toLowerCase();$$("dl div").forEach(function(d){d.style.display=d.textContent.toLowerCase().indexOf(t)>-1?"":"none"})};
var w=$("#wa");if(w)w.href="https://wa.me/?text="+encodeURIComponent(document.title+" "+location.href);
var s=$("#ig");if(s)s.onclick=function(){if(navigator.share){navigator.share({title:document.title,url:location.href})}else{try{navigator.clipboard.writeText(location.href)}catch(e){}alert("Link copiado! Cole nos Stories, na bio ou em uma mensagem do Instagram.")}};
var cp=$("#cp");if(cp)cp.onclick=function(){try{navigator.clipboard.writeText(location.href);cp.textContent="✅ Copiado!"}catch(e){}};
var Q=$("#quiz");if(Q){var D=JSON.parse($("#qdata").textContent),pts=0,n=0;D.forEach(function(x,i){var d=document.createElement("div");d.className="q";d.innerHTML="<b>"+(i+1)+". "+x.q+"</b><div class='row'><button class='btn o' data-v='1'>Verdade</button><button class='btn o' data-v='0'>Mito</button></div><div class='res'></div>";
$$("button",d).forEach(function(b){b.onclick=function(){if(d.dataset.done)return;d.dataset.done=1;n++;var ok=(b.dataset.v=="1")==x.r;if(ok)pts++;$(".res",d).innerHTML=(ok?"<b class='ok'>Acertou!</b> ":"<b class='no'>Quase!</b> ")+x.e;if(n==D.length)$("#score").textContent="Você fez "+pts+" de "+D.length+" pontos! 🌸"}});Q.appendChild(d)})}
})();
