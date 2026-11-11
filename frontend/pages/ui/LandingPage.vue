<template>
  <q-layout view="lHh Lpr lFf" class="landing-layout">
    <q-header class="landing-header" flat>
      <q-toolbar class="container">
        <div class="logo">
          <div class="logo-mark"><q-icon name="ads_click" size="20px" /></div>
          <span>SkillSnap</span>
        </div>
        <q-space />
        <nav class="landing-nav gt-sm">
          <a href="#how" class="nav-link">Как это работает</a>
          <a href="#features" class="nav-link">Возможности</a>
          <a href="#team" class="nav-link">Команда</a>
        </nav>
        <q-space />
        <q-btn flat no-caps color="dark" label="Войти" to="/login" class="text-weight-medium" />
        <q-btn
          unelevated
          no-caps
          color="primary"
          label="Начать бесплатно"
          to="/registration"
          class="text-weight-bold header-cta"
        />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="landing-page">

        <!-- ======= HERO ======= -->
        <section class="hero">
          <div class="container hero-grid">
            <div class="hero-copy">
              <div class="hero-badge">
                <span class="hero-badge-dot"></span>
                Интерактивные тренажёры для корпоративного обучения
              </div>
              <h1 class="hero-title">
                Научите сотрудников работать в ПО — <span class="text-gradient">на практике</span>, а не по инструкциям
              </h1>
              <p class="hero-subtitle">
                SkillSnap превращает скриншоты и материалы компании в пошаговые симуляторы:
                пользователь кликает, вводит текст и проходит реальный сценарий — в безопасной среде, без риска что-то сломать.
              </p>
              <div class="hero-actions">
                <q-btn
                  unelevated
                  no-caps
                  color="primary"
                  size="lg"
                  label="Попробовать демо"
                  to="/login"
                  class="hero-btn-primary"
                />
                <q-btn
                  outline
                  no-caps
                  color="primary"
                  size="lg"
                  label="Обсудить пилот"
                  href="mailto:hello@skillsnap.ru"
                  class="hero-btn-secondary"
                />
              </div>
              <div class="hero-markers">
                <div class="hero-marker" v-for="m in markers" :key="m">
                  <q-icon name="check_circle" size="18px" color="positive" />
                  <span>{{ m }}</span>
                </div>
              </div>
            </div>

            <!-- Макет продукта -->
            <div class="hero-visual" aria-hidden="true">
              <div class="mock-window">
                <div class="mock-window-bar">
                  <span class="mock-dot mock-dot--red"></span>
                  <span class="mock-dot mock-dot--yellow"></span>
                  <span class="mock-dot mock-dot--green"></span>
                  <div class="mock-url">skillsnap.ru/training</div>
                </div>
                <div class="mock-body">
                  <div class="mock-sidebar">
                    <div class="mock-line mock-line--strong"></div>
                    <div class="mock-line"></div>
                    <div class="mock-line"></div>
                    <div class="mock-line mock-line--short"></div>
                  </div>
                  <div class="mock-screen">
                    <div class="mock-toolbar"></div>
                    <div class="mock-content">
                      <div class="mock-block"></div>
                      <div class="mock-block mock-block--wide"></div>
                      <div class="mock-hotspot">
                        <span class="mock-hotspot-ring"></span>
                      </div>
                      <div class="mock-block"></div>
                    </div>
                    <div class="mock-hint">
                      <q-icon name="ads_click" size="16px" color="primary" />
                      Нажмите «Отправка и получение»
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- ======= ДО / ПОСЛЕ ======= -->
        <section class="section">
          <div class="container">
            <div class="section-header">
              <div class="section-tag">Зачем</div>
              <h2 class="section-title">Видео учит смотреть.<br/>Симулятор учит делать.</h2>
              <p class="section-subtitle">
                Сотрудник не запоминает интерфейс по PDF — он запоминает его руками.
              </p>
            </div>
            <div class="compare-grid">
              <div class="compare-card compare-card--before">
                <div class="compare-label compare-label--before">Обычно</div>
                <div class="compare-heading">
                  <q-icon name="description" size="28px" color="grey-6" />
                  Инструкция в PDF
                </div>
                <ul class="compare-list">
                  <li><q-icon name="close" color="negative" size="16px" />Читают один раз и забывают</li>
                  <li><q-icon name="close" color="negative" size="16px" />Нет практики и обратной связи</li>
                  <li><q-icon name="close" color="negative" size="16px" />Ошибки — уже в боевой системе</li>
                  <li><q-icon name="close" color="negative" size="16px" />Прогресс не измерить</li>
                </ul>
              </div>
              <div class="compare-card compare-card--after">
                <div class="compare-label compare-label--after">Со SkillSnap</div>
                <div class="compare-heading">
                  <q-icon name="ads_click" size="28px" color="primary" />
                  Интерактивный симулятор
                </div>
                <ul class="compare-list">
                  <li><q-icon name="check" color="positive" size="16px" />Пошаговая практика на скриншотах</li>
                  <li><q-icon name="check" color="positive" size="16px" />Подсказки после ошибки</li>
                  <li><q-icon name="check" color="positive" size="16px" />Безопасная среда без последствий</li>
                  <li><q-icon name="check" color="positive" size="16px" />Статистика прохождений</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <!-- ======= КАК ЭТО РАБОТАЕТ ======= -->
        <section class="section section--alt" id="how">
          <div class="container">
            <div class="section-header">
              <div class="section-tag">Процесс</div>
              <h2 class="section-title">От материалов до тренажёра —<br/>за один день</h2>
            </div>
            <div class="steps-grid">
              <div class="step-card" v-for="(s, i) in steps" :key="s.title">
                <div class="step-num">{{ String(i + 1).padStart(2, '0') }}</div>
                <div class="step-icon"><q-icon :name="s.icon" size="26px" color="primary" /></div>
                <div class="step-title">{{ s.title }}</div>
                <div class="step-desc">{{ s.desc }}</div>
              </div>
            </div>
          </div>
        </section>

        <!-- ======= ВОЗМОЖНОСТИ ======= -->
        <section class="section" id="features">
          <div class="container">
            <div class="section-header">
              <div class="section-tag">Возможности</div>
              <h2 class="section-title">Всё для запуска<br/>обучения в компании</h2>
            </div>
            <div class="features-grid">
              <div class="feature-card" v-for="f in features" :key="f.title">
                <div class="feature-icon" :style="{ background: f.bg, color: f.color }">
                  <q-icon :name="f.icon" size="22px" />
                </div>
                <div class="feature-title">{{ f.title }}</div>
                <div class="feature-desc">{{ f.desc }}</div>
              </div>
            </div>
          </div>
        </section>

        <!-- ======= КОМАНДА ======= -->
        <section class="section section--alt" id="team">
          <div class="container">
            <div class="section-header">
              <div class="section-tag">Команда</div>
              <h2 class="section-title">Кто делает продукт</h2>
            </div>
            <div class="team-grid">
              <div class="team-card" v-for="member in team" :key="member.name">
                <div class="team-avatar">
                  <img :src="member.photo" :alt="member.name" />
                </div>
                <div class="team-name">{{ member.name }}</div>
                <div class="team-role">{{ member.role }}</div>
                <div class="team-bio">{{ member.bio }}</div>
              </div>
            </div>
          </div>
        </section>

        <!-- ======= CTA ======= -->
        <section class="section">
          <div class="container">
            <div class="cta-card">
              <h2 class="cta-title">Запустите первый тренажёр уже сегодня</h2>
              <p class="cta-subtitle">
                Покажем демо на ваших материалах и обсудим пилотный проект.
              </p>
              <div class="cta-actions">
                <q-btn
                  unelevated
                  no-caps
                  color="white"
                  text-color="primary"
                  size="lg"
                  label="Начать бесплатно"
                  to="/registration"
                  class="text-weight-bold cta-btn-primary"
                />
                <q-btn
                  outline
                  no-caps
                  color="white"
                  size="lg"
                  label="Написать нам"
                  href="mailto:hello@skillsnap.ru"
                  class="cta-btn-secondary"
                />
              </div>
            </div>
          </div>
        </section>

        <!-- ======= FOOTER ======= -->
        <footer class="landing-footer">
          <div class="container footer-inner">
            <div class="logo logo--footer">
              <div class="logo-mark"><q-icon name="ads_click" size="18px" /></div>
              <span>SkillSnap</span>
            </div>
            <div class="footer-copy">© {{ new Date().getFullYear() }} SkillSnap. Интерактивные тренажёры для бизнеса.</div>
            <a class="footer-mail" href="mailto:hello@skillsnap.ru">hello@skillsnap.ru</a>
          </div>
        </footer>

      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue';

const markers = ref([
  'Практика вместо PDF и видео',
  'Запуск без интеграций',
  'On-premise и корпоративный контур',
]);

const steps = ref([
  {
    icon: 'upload_file',
    title: 'Загружаете материалы',
    desc: 'Скриншоты, инструкции, записи экрана — то, что уже есть у компании.',
  },
  {
    icon: 'dashboard_customize',
    title: 'Собираете сценарий',
    desc: 'В редакторе размечаете области, действия и ветвления — без кода.',
  },
  {
    icon: 'school',
    title: 'Сотрудник проходит тренинг',
    desc: 'Пошаговая практика: клики, ввод текста, горячие клавиши — как в реальной системе.',
  },
  {
    icon: 'monitoring',
    title: 'Видите результат',
    desc: 'Статистика прохождений, ошибки по шагам, время — всё измеримо.',
  },
]);

const features = ref([
  {
    icon: 'ads_click',
    title: 'Интерактивные шаги',
    desc: 'Клики, двойные клики, наведение, ввод текста и хоткеи с проверкой правильности.',
    bg: 'rgba(79, 70, 229, 0.1)', color: '#4f46e5',
  },
  {
    icon: 'account_tree',
    title: 'Ветвящиеся сценарии',
    desc: 'Визуальный граф переходов: разные пути по успеху, ошибке или условию.',
    bg: 'rgba(8, 145, 178, 0.1)', color: '#0891b2',
  },
  {
    icon: 'lightbulb',
    title: 'Подсказки после ошибки',
    desc: 'Подсветка области и автоподстановка текста — пользователь не застревает.',
    bg: 'rgba(217, 119, 6, 0.1)', color: '#d97706',
  },
  {
    icon: 'link',
    title: 'Публичные ссылки',
    desc: 'Прохождение без регистрации — отправили ссылку, человек тренируется.',
    bg: 'rgba(124, 58, 237, 0.1)', color: '#7c3aed',
  },
  {
    icon: 'monitoring',
    title: 'Аналитика прохождений',
    desc: 'Кто прошёл, где ошибался, сколько времени заняло — по каждой попытке.',
    bg: 'rgba(5, 150, 105, 0.1)', color: '#059669',
  },
  {
    icon: 'business',
    title: 'Организации и сотрудники',
    desc: 'Структура компании, роли и выдача тренингов команде.',
    bg: 'rgba(220, 38, 127, 0.1)', color: '#be185d',
  },
]);

const team = ref([
  {
    name: 'Абарникова Елена',
    role: 'Founder · Product',
    photo: '/team/abarnikova.png',
    bio: '20+ лет в EdTech и корпоративном обучении. Продуктовая стратегия и методология. Победитель хакатона «Лидеры цифровой трансформации-2024».',
  },
  {
    name: 'Сидорин Тимофей',
    role: 'Co-founder · Backend / ML',
    photo: '/team/sidorin.png',
    bio: 'Серверная часть и надёжность платформы. Призёр «Лидеры цифровой трансформации 2024 ЯКУТИЯ» и Гагарин Хакатона 2024.',
  },
  {
    name: 'Черненко Константин',
    role: 'Frontend / UX-UI',
    photo: '/team/chernenko.png',
    bio: 'Интерфейсы сложных веб-приложений. Фокус — удобство для методистов и пользователей. Призёр «Лидеры цифровой трансформации 2024 ЯКУТИЯ».',
  },
]);
</script>

<script>
export default { name: 'LandingPage' };
</script>

<style scoped>
/* ==================== BASE ==================== */
.landing-layout {
  background: #fff;
}
.container {
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 32px;
}

/* ==================== HEADER ==================== */
.landing-header {
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}
.landing-header .q-toolbar {
  min-height: 68px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 800;
  letter-spacing: -0.5px;
  color: #0f172a;
}
.logo-mark {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35);
}
.landing-nav {
  display: flex;
  gap: 28px;
}
.nav-link {
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  text-decoration: none;
  transition: color 0.2s;
}
.nav-link:hover { color: #4f46e5; }
.header-cta { border-radius: 10px; }

/* ==================== TYPO ==================== */
.text-gradient {
  background: linear-gradient(120deg, #4f46e5, #7c3aed 55%, #0891b2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.section-tag {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.6px;
  text-transform: uppercase;
  color: #4f46e5;
  margin-bottom: 18px;
}
.section-title {
  font-size: clamp(1.9rem, 3.6vw, 2.7rem);
  font-weight: 800;
  line-height: 1.15;
  letter-spacing: -0.8px;
  color: #0f172a;
  margin: 0 0 16px;
}
.section-subtitle {
  font-size: 1.08rem;
  color: #64748b;
  max-width: 620px;
  margin: 0 auto;
  line-height: 1.65;
}
.section-header { text-align: center; margin-bottom: 56px; }

/* ==================== HERO ==================== */
.hero {
  position: relative;
  padding: 96px 0 110px;
  overflow: hidden;
  background:
    radial-gradient(60% 50% at 15% 0%, rgba(79, 70, 229, 0.09), transparent 70%),
    radial-gradient(50% 45% at 90% 20%, rgba(8, 145, 178, 0.08), transparent 70%);
}
.hero-grid {
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  gap: 64px;
  align-items: center;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  font-size: 13px;
  font-weight: 600;
  color: #4338ca;
  background: rgba(79, 70, 229, 0.08);
  border: 1px solid rgba(79, 70, 229, 0.18);
  border-radius: 999px;
  padding: 8px 18px;
  margin-bottom: 28px;
}
.hero-badge-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #4f46e5;
  animation: hero-pulse 2s infinite;
}
@keyframes hero-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.45; transform: scale(0.75); }
}
.hero-title {
  font-size: clamp(2.3rem, 4.4vw, 3.6rem);
  font-weight: 850;
  line-height: 1.08;
  letter-spacing: -1.6px;
  color: #0f172a;
  margin: 0 0 22px;
}
.hero-subtitle {
  font-size: 1.14rem;
  color: #475569;
  line-height: 1.65;
  margin: 0 0 34px;
  max-width: 560px;
}
.hero-actions { display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 34px; }
.hero-btn-primary {
  border-radius: 12px;
  box-shadow: 0 10px 24px rgba(79, 70, 229, 0.3);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.hero-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 32px rgba(79, 70, 229, 0.42);
}
.hero-btn-secondary {
  border-radius: 12px;
  transition: transform 0.25s ease;
}
.hero-btn-secondary:hover { transform: translateY(-2px); }
.hero-markers {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 22px;
}
.hero-marker {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

/* Макет продукта */
.hero-visual { position: relative; }
.mock-window {
  border-radius: 16px;
  background: #fff;
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow:
    0 24px 60px rgba(15, 23, 42, 0.14),
    0 0 0 1px rgba(255, 255, 255, 0.6) inset;
  overflow: hidden;
  transform: perspective(1400px) rotateY(-7deg) rotateX(3deg);
  transition: transform 0.6s ease;
}
.hero-visual:hover .mock-window {
  transform: perspective(1400px) rotateY(-3deg) rotateX(1deg);
}
.mock-window-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  background: #f8fafc;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}
.mock-dot { width: 10px; height: 10px; border-radius: 50%; }
.mock-dot--red { background: #fca5a5; }
.mock-dot--yellow { background: #fcd34d; }
.mock-dot--green { background: #86efac; }
.mock-url {
  margin-left: 12px;
  font-size: 11px;
  color: #94a3b8;
  background: #fff;
  border: 1px solid rgba(15, 23, 42, 0.07);
  border-radius: 6px;
  padding: 2px 10px;
}
.mock-body { display: flex; height: 320px; }
.mock-sidebar {
  width: 148px;
  padding: 16px 14px;
  background: #f8fafc;
  border-right: 1px solid rgba(15, 23, 42, 0.06);
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.mock-line {
  height: 9px;
  border-radius: 5px;
  background: #e2e8f0;
}
.mock-line--strong { background: #c7d2fe; }
.mock-line--short { width: 60%; }
.mock-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 14px;
  gap: 12px;
  position: relative;
}
.mock-toolbar {
  height: 26px;
  border-radius: 8px;
  background: linear-gradient(90deg, #eef2ff, #f8fafc);
}
.mock-content {
  flex: 1;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.mock-block {
  height: 26px;
  border-radius: 7px;
  background: #f1f5f9;
}
.mock-block--wide { width: 70%; }
.mock-hotspot {
  position: relative;
  height: 34px;
  width: 55%;
  border-radius: 8px;
  border: 2px solid #4f46e5;
  background: rgba(79, 70, 229, 0.1);
}
.mock-hotspot-ring {
  position: absolute;
  top: -6px; right: -6px;
  width: 16px; height: 16px;
  border-radius: 50%;
  background: #4f46e5;
  animation: hotspot-ping 1.6s cubic-bezier(0, 0, 0.2, 1) infinite;
}
@keyframes hotspot-ping {
  0% { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.5); }
  80%, 100% { box-shadow: 0 0 0 14px rgba(79, 70, 229, 0); }
}
.mock-hint {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  align-self: flex-start;
  font-size: 12px;
  font-weight: 600;
  color: #0f172a;
  background: #eef2ff;
  border: 1px solid rgba(79, 70, 229, 0.2);
  border-radius: 999px;
  padding: 7px 14px;
}

/* ==================== SECTIONS ==================== */
.section { padding: 96px 0; }
.section--alt { background: #f8fafc; }

/* До / после */
.compare-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  max-width: 940px;
  margin: 0 auto;
}
.compare-card {
  border-radius: 20px;
  padding: 32px;
  border: 1px solid rgba(15, 23, 42, 0.07);
}
.compare-card--before { background: #fafafa; }
.compare-card--after {
  background: #fff;
  border-color: rgba(79, 70, 229, 0.25);
  box-shadow: 0 16px 40px rgba(79, 70, 229, 0.1);
}
.compare-label {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  border-radius: 999px;
  padding: 4px 14px;
  margin-bottom: 18px;
}
.compare-label--before { background: #fee2e2; color: #b91c1c; }
.compare-label--after { background: #e0e7ff; color: #4338ca; }
.compare-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 17px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 18px;
}
.compare-list {
  list-style: none;
  margin: 0; padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.compare-list li {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 14px;
  color: #475569;
}

/* Шаги */
.steps-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}
.step-card {
  position: relative;
  background: #fff;
  border: 1px solid rgba(15, 23, 42, 0.07);
  border-radius: 18px;
  padding: 28px 24px;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}
.step-card:hover {
  transform: translateY(-4px);
  border-color: rgba(79, 70, 229, 0.3);
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.09);
}
.step-num {
  position: absolute;
  top: 20px; right: 22px;
  font-size: 34px;
  font-weight: 800;
  color: #eef2ff;
  line-height: 1;
}
.step-icon {
  width: 48px; height: 48px;
  border-radius: 13px;
  background: rgba(79, 70, 229, 0.09);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}
.step-title { font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 8px; }
.step-desc { font-size: 13.5px; color: #64748b; line-height: 1.55; }

/* Фичи */
.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}
.feature-card {
  background: #fff;
  border: 1px solid rgba(15, 23, 42, 0.07);
  border-radius: 18px;
  padding: 26px 24px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.08);
}
.feature-icon {
  width: 44px; height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}
.feature-title { font-size: 15.5px; font-weight: 700; color: #0f172a; margin-bottom: 7px; }
.feature-desc { font-size: 13.5px; color: #64748b; line-height: 1.55; }

/* Команда */
.team-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
  max-width: 1000px;
  margin: 0 auto;
}
.team-card {
  background: #fff;
  border: 1px solid rgba(15, 23, 42, 0.07);
  border-radius: 20px;
  padding: 30px 26px;
  text-align: center;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.team-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.09);
}
.team-avatar {
  width: 96px; height: 96px;
  margin: 0 auto 18px;
  border-radius: 26px;
  overflow: hidden;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.14);
}
.team-avatar img {
  width: 100%; height: 100%;
  object-fit: cover;
  display: block;
}
.team-name { font-size: 17px; font-weight: 800; color: #0f172a; margin-bottom: 4px; }
.team-role {
  font-size: 12.5px;
  font-weight: 700;
  letter-spacing: 0.4px;
  color: #4f46e5;
  text-transform: uppercase;
  margin-bottom: 14px;
}
.team-bio {
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
  text-align: left;
}

/* CTA */
.cta-card {
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  padding: 72px 48px;
  text-align: center;
  color: #fff;
  background: linear-gradient(135deg, #312e81, #4f46e5 45%, #7c3aed 90%);
}
.cta-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(45% 60% at 80% 10%, rgba(255, 255, 255, 0.16), transparent 70%),
    radial-gradient(40% 55% at 10% 90%, rgba(8, 145, 178, 0.35), transparent 70%);
}
.cta-title {
  position: relative;
  font-size: clamp(1.7rem, 3.2vw, 2.4rem);
  font-weight: 800;
  letter-spacing: -0.6px;
  margin: 0 0 14px;
}
.cta-subtitle {
  position: relative;
  font-size: 1.05rem;
  color: rgba(255, 255, 255, 0.82);
  margin: 0 0 34px;
}
.cta-actions {
  position: relative;
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 14px;
}
.cta-btn-primary {
  border-radius: 12px;
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.25);
}
.cta-btn-secondary { border-radius: 12px; }

/* Footer */
.landing-footer {
  border-top: 1px solid rgba(15, 23, 42, 0.06);
  padding: 28px 0;
  background: #fff;
}
.footer-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 14px;
}
.logo--footer { font-size: 16px; }
.logo--footer .logo-mark { width: 28px; height: 28px; border-radius: 8px; }
.footer-copy { font-size: 13px; color: #94a3b8; }
.footer-mail {
  font-size: 13px;
  font-weight: 600;
  color: #4f46e5;
  text-decoration: none;
}
.footer-mail:hover { text-decoration: underline; }

/* ==================== RESPONSIVE ==================== */
@media (max-width: 1024px) {
  .hero-grid { grid-template-columns: 1fr; gap: 56px; }
  .hero-visual { max-width: 620px; margin: 0 auto; width: 100%; }
  .mock-window { transform: none; }
  .steps-grid { grid-template-columns: repeat(2, 1fr); }
  .features-grid { grid-template-columns: repeat(2, 1fr); }
  .team-grid { grid-template-columns: 1fr; max-width: 460px; }
}
@media (max-width: 640px) {
  .container { padding: 0 20px; }
  .hero { padding: 64px 0 72px; }
  .section { padding: 64px 0; }
  .compare-grid { grid-template-columns: 1fr; }
  .steps-grid,
  .features-grid { grid-template-columns: 1fr; }
  .cta-card { padding: 48px 24px; }
  .mock-sidebar { display: none; }
}
</style>
