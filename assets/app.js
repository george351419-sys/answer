import {getState, formatTime} from './timing.js';
const $ = id => document.getElementById(id);
const question = JSON.parse($('question').textContent);
if (!question) {
  $('missing').hidden = false;
} else {
  $('puzzle').hidden = false;
  $('title').textContent = question.title;
  document.title = `${question.title} · 小玩学家`;
  $('second').hidden = !question.hint2;
  // Content and timing changes create a fresh visit, without affecting other puzzles.
  const key = 'little-player:v1:' + JSON.stringify(question);
  const now = Date.now();
  let start = now;
  try {
    const saved = Number(localStorage.getItem(key));
    if (Number.isFinite(saved) && saved > 0 && saved <= now) start = saved;
    else localStorage.setItem(key, String(start));
  } catch {
    $('footnote').textContent = '提示会自动出现。当前浏览器无法保存进度，请保持本页打开。';
  }
  let firstShown = false, secondShown = false;
  function render() {
    const state = getState(start, Date.now(), question.delay1, question.delay2, Boolean(question.hint2));
    $('timer1').textContent = formatTime(state.remaining1);
    $('dial').style.setProperty('--progress', `${state.progress}%`);
    if (state.first && !firstShown) {
      firstShown = true;
      $('wait1').hidden = true; $('bottom1').hidden = true;
      $('hint1').textContent = question.hint1; $('hint1').hidden = false;
      $('hint1').setAttribute('role', 'status'); $('status1').textContent = '已解锁';
    }
    if (question.hint2) {
      $('timer2').textContent = state.first ? formatTime(state.remaining2) : '';
      if (state.first) {
        $('status2').textContent = state.second ? '已解锁' : '思考时间';
        $('second-pending').hidden = true;
        $('wait2').hidden = state.second;
        $('second').classList.remove('secondary');
        $('second').classList.add('active');
        const progress2 = Math.max(0, Math.min(100, (Date.now() - start - question.delay1 * 1000) / (question.delay2 * 1000) * 100));
        $('dial2').style.setProperty('--progress', `${progress2}%`);
      }
      if (state.second && !secondShown) {
        secondShown = true; $('wait2').hidden = true;
        $('hint2').textContent = question.hint2; $('hint2').hidden = false;
        $('hint2').setAttribute('role', 'status');
      }
    }
  }
  render();
  const interval = setInterval(() => {render(); if (firstShown && (!question.hint2 || secondShown)) clearInterval(interval);}, 250);
  document.addEventListener('visibilitychange', render);
  window.addEventListener('pageshow', render);
}
