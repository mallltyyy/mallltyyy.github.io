// Рассрочка DIRHAM: расчёт и виджет выбора срока. Общий для index.html и rassrochka.html.
// Наценки (с сайта dirham95.ru): без взноса 12/22/30/40%, со взносом 9/15/22/30%.
// Формула подобрана по их калькулятору: (цена × (1 + наценка) − взнос) / срок, вниз до 50 ₽.
var RS = {
  MIN: 25000,
  N: [3, 6, 9, 12],
  M0: { 3: 12, 6: 22, 9: 30, 12: 40 },
  M1: { 3: 9, 6: 15, 9: 22, 12: 30 },
  AUTO: 0.23,
  WA: "https://wa.me/79280040943?text=",
  fmt: function (n) { return Math.round(n).toLocaleString("ru-RU").replace(/ /g, " ") + " ₽"; },
  autoDown: function (pr) { return Math.round(pr * RS.AUTO / 50) * 50; },
  month: function (pr, n, down) {
    var m = (down > 0 ? RS.M1 : RS.M0)[n];
    return Math.max(0, Math.floor((pr * (1 + m / 100) - (down || 0)) / n / 50) * 50);
  },
  from: function (pr) { return RS.month(pr, 12, 0); },
  // Рисует виджет в el. opts: {price, getText(state)->string, btn:"Оформить в рассрочку", docs:true}
  mount: function (el, opts) {
    var st = { n: 12, dn: false, down: RS.autoDown(opts.price), price: opts.price };
    function body() {
      var pr = st.price, d = st.dn ? st.down : 0;
      return RS.N.map(function (n) {
        var m = (st.dn ? RS.M1 : RS.M0)[n];
        return '<button type="button" class="rsrow' + (n === st.n ? ' on' : '') + '" data-n="' + n + '"><span>' + n + ' мес.</span><b>≈ ' + RS.fmt(RS.month(pr, n, d)) + '<small>/мес</small></b><em>+' + m + '%</em></button>';
      }).join("") +
        '<div class="rssum">Итого к оплате: <b>≈ ' + RS.fmt(RS.month(pr, st.n, d) * st.n + d) + '</b>' + (d ? '<br>взнос ' + RS.fmt(d) + ' + ' + st.n + ' × ' + RS.fmt(RS.month(pr, st.n, d)) : '') + '</div>' +
        '<a class="rsbtn" target="_blank" rel="noopener" href="' + RS.WA + encodeURIComponent(opts.getText(RS.state(st))) + '">' + (opts.btn || 'Оформить в рассрочку') + '</a>';
    }
    function draw() {
      el.innerHTML =
        '<div class="rsseg"><button type="button" data-dn="0" class="' + (st.dn ? '' : 'on') + '">Без взноса</button><button type="button" data-dn="1" class="' + (st.dn ? 'on' : '') + '">Со взносом</button></div>' +
        (st.dn ? '<label class="rsdown">Первый взнос, ₽<input type="number" inputmode="numeric" min="0" step="500" value="' + st.down + '"></label>' : '') +
        '<div class="rsbody">' + body() + '</div>' +
        (opts.docs !== false ? '<small class="rsnote">Нужно: возраст от 20 лет, прописка в ЧР, паспорт и номер телефона покупателя и поручителя. Расчёт примерный, точную сумму и одобрение даёт DIRHAM. <a href="https://tehnoodom.github.io/rassrochka.html" target="_blank" rel="noopener">Подробнее о рассрочке</a></small>' : '');
    }
    el.onclick = function (e) {
      var a = e.target.closest(".rsbtn");
      if (a) { if (opts.check && !opts.check()) { e.preventDefault(); return; } a.href = RS.WA + encodeURIComponent(opts.getText(RS.state(st))); return; }
      var b = e.target.closest("button"); if (!b) return;
      if (b.dataset.n) { st.n = +b.dataset.n; el.querySelector(".rsbody").innerHTML = body(); }
      else if (b.dataset.dn) { st.dn = b.dataset.dn === "1"; draw(); }
    };
    el.oninput = function (e) {
      if (e.target.type !== "number") return;
      st.down = Math.max(0, Math.min(st.price * 0.9, +e.target.value || 0));
      el.querySelector(".rsbody").innerHTML = body();
    };
    draw();
    return { set: function (pr) { st.price = pr; st.down = RS.autoDown(pr); draw(); }, redraw: function () { var x = el.querySelector('.rsbody'); if (x) x.innerHTML = body(); } };
  },
  state: function (st) {
    var d = st.dn ? st.down : 0;
    return { n: st.n, down: d, month: RS.month(st.price, st.n, d), line: "Срок: " + st.n + " мес.\n" + (d ? "Первый взнос: " + RS.fmt(d) + "\n" : "Без первого взноса\n") + "Платёж: ≈ " + RS.fmt(RS.month(st.price, st.n, d)) + " в месяц" };
  }
};
