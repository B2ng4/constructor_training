<template>
  <q-layout view="lHh Lpr lFf" class="landing-layout">
    <!-- Header with Auth Links -->
    <q-header class="landing-header" flat>
      <q-toolbar class="container q-py-md">
        <div class="text-h5 text-weight-bolder text-primary" style="letter-spacing: -0.5px;">SkillSnap</div>
        <q-space />
        <q-btn flat color="dark" label="Войти" to="/login" class="text-weight-bold q-mr-sm" />
        <q-btn unelevated color="primary" label="Регистрация" to="/registration" rounded class="text-weight-bold" />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page class="landing-page relative-position overflow-hidden">

        <!-- Background Blobs -->
        <div class="blob-bg blob-1"></div>
        <div class="blob-bg blob-2"></div>
        <div class="blob-bg blob-3"></div>

        <!-- ======= 1. HERO SECTION ======= -->
        <section class="hero-section">
          <div class="container">
            <div class="hero-tag animate-fade-in-up animate-stagger-1">
              <span class="tag-dot"></span>
              Корпоративное обучение нового поколения
            </div>

            <h1 class="hero-title animate-fade-in-up animate-stagger-2">
              SkillSnap — <span class="text-gradient">тренажёры</span><br/>
              для обучения работе в ПО
            </h1>

            <p class="hero-subtitle animate-fade-in-up animate-stagger-3">
              Превращаем скриншоты, инструкции и материалы компании в интерактивные симуляторы,
              которые помогают сотрудникам не просто изучить интерфейс, а начать уверенно работать в системе.
            </p>

            <div class="hero-markers animate-fade-in-up animate-stagger-3">
              <div class="marker-item" v-for="m in markers" :key="m">
                <q-icon name="check_circle" color="primary" size="18px" />
                <span>{{ m }}</span>
              </div>
            </div>

            <div class="hero-actions animate-fade-in-up animate-stagger-4">
              <q-btn
                unelevated
                rounded
                color="primary"
                label="Запустить демо"
                size="lg"
                class="hero-btn hero-btn--primary q-px-xl text-weight-bold"
                to="/login"
              />
              <q-btn
                outline
                rounded
                color="primary"
                size="lg"
                class="hero-btn hero-btn--outline q-px-xl"
                @click="openVideoDialog"
              >
                <q-icon name="play_circle_outline" class="q-mr-sm" />
                Посмотреть, как это работает
              </q-btn>
              <q-btn
                flat
                rounded
                color="grey-8"
                label="Обсудить пилот"
                size="lg"
                class="hero-btn q-px-xl"
                href="mailto:hello@skillsnap.ru"
              />
            </div>
          </div>
        </section>

        <!-- ======= 2. HOW IT WORKS ======= -->
        <section class="section-how bg-white">
          <div class="container">
            <div class="section-header text-center q-mb-xl">
              <div class="section-tag">Решение</div>
              <h2 class="section-title">
                Видео учит смотреть,<br/>
                <span class="text-gradient">симулятор — делать</span>
              </h2>
              <p class="section-subtitle">
                SkillSnap помогает собирать интерактивные тренажёры из материалов клиента
                и обучать сотрудников через пошаговую практику в интерфейсе.
              </p>
            </div>

            <div class="how-grid">
              <!-- Left: short description -->
              <div class="how-left">
                <div class="before-after-card glass-card">
                  <div class="ba-col ba-before">
                    <div class="ba-label ba-label--before">До</div>
                    <div class="ba-icon">📄</div>
                    <div class="ba-heading">Обычная инструкция</div>
                    <ul class="ba-list">
                      <li>Статичный PDF</li>
                      <li>Нет практики</li>
                      <li>Сотрудник читает, но не делает</li>
                      <li>Нет обратной связи</li>
                    </ul>
                  </div>
                  <div class="ba-divider">
                    <q-icon name="arrow_forward" color="primary" size="28px" />
                  </div>
                  <div class="ba-col ba-after">
                    <div class="ba-label ba-label--after">После</div>
                    <div class="ba-icon">🎯</div>
                    <div class="ba-heading">SkillSnap симулятор</div>
                    <ul class="ba-list">
                      <li>Интерактивный сценарий</li>
                      <li>Пошаговая практика</li>
                      <li>Сотрудник делает сам</li>
                      <li>Аналитика и прогресс</li>
                    </ul>
                  </div>
                </div>
              </div>

              <!-- Right: 4 steps -->
              <div class="how-right">
                <div
                  class="step-item"
                  v-for="(step, idx) in steps"
                  :key="idx"
                >
                  <div class="step-number" :style="{ background: step.gradient }">
                    {{ idx + 1 }}
                  </div>
                  <div class="step-connector" v-if="idx < steps.length - 1"></div>
                  <div class="step-body">
                    <div class="step-title">{{ step.title }}</div>
                    <div class="step-desc">{{ step.desc }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- ======= 3. TECH + METRICS ======= -->
        <section class="section-tech">
          <div class="container">
            <div class="section-header text-center q-mb-xl">
              <div class="section-tag">Технология и метрики</div>
              <h2 class="section-title">
                Технология, которую<br/>
                <span class="text-gradient">можно измерить</span>
              </h2>
            </div>

            <div class="tech-grid">
              <!-- Left: Technology -->
              <div class="tech-left glass-card">
                <div class="tech-block-title">
                  <q-icon name="memory" color="primary" size="28px" class="q-mr-sm" />
                  Технологии
                </div>
                <div class="tech-list">
                  <div class="tech-list-item" v-for="t in techList" :key="t.text">
                    <div class="tech-bullet" :style="{ background: t.color }"></div>
                    <span>{{ t.text }}</span>
                  </div>
                </div>
              </div>

              <!-- Right: Metrics -->
              <div class="tech-right">
                <div
                  class="metric-card glass-card"
                  v-for="m in metrics"
                  :key="m.label"
                >
                  <div class="metric-value" :style="{ color: m.color }">{{ m.value }}</div>
                  <div class="metric-label">{{ m.label }}</div>
                </div>
              </div>
            </div>

            <div class="tech-footer">
              В ядре — повторяемая SaaS-логика, а рост подтверждается продуктовой и коммерческой метрикой.
            </div>
          </div>
        </section>

        <!-- ======= 4. TEAM SECTION ======= -->
        <section class="section-team bg-white">
          <div class="container">
            <div class="section-header text-center q-mb-xl">
              <div class="section-tag">Команда</div>
              <h2 class="section-title">Создатели платформы</h2>
              <p class="section-subtitle">Люди, которые воплощают амбициозные идеи в реальность.</p>
            </div>

            <div class="row q-col-gutter-xl justify-center">
              <div class="col-12 col-md-6 col-lg-4" v-for="member in team" :key="member.name">
                <q-card flat class="team-card glass-card-solid full-height flex column">
                  <div class="row justify-center q-mt-lg q-mb-md">
                    <div class="team-squircle shadow-4">
                      <img :src="member.photo" class="team-image" />
                    </div>
                  </div>
                  <q-card-section class="q-pt-sm q-pb-xl q-px-lg flex-grow-1 text-center">
                    <div class="text-h5 text-weight-bolder q-mb-xs text-dark">{{ member.name }}</div>
                    <div class="team-role q-mb-md" :style="{ color: member.roleColor }">{{ member.role }}</div>
                    <q-separator class="q-mb-md" />
                    <div class="text-body2 text-grey-8 desc-text text-left">{{ member.bio }}</div>
                  </q-card-section>
                </q-card>
              </div>
            </div>
          </div>
        </section>

        <!-- ======= 5. CTA SECTION ======= -->
        <section class="section-cta">
          <div class="container">
            <div class="cta-card">
              <div class="cta-glow"></div>
              <div class="cta-content">
                <h2 class="cta-title">Готовы запустить первый симулятор?</h2>
                <p class="cta-subtitle">
                  Свяжитесь с нами — обсудим вашу задачу и покажем демо на реальных данных.
                </p>
                <div class="cta-actions">
                  <q-btn
                    unelevated
                    color="white"
                    text-color="primary"
                    label="Запустить демо"
                    size="lg"
                    class="text-weight-bold hero-btn q-px-xl shadow-4"
                    to="/login"
                    rounded
                  />
                  <q-btn
                    outline
                    color="white"
                    label="Обсудить пилот"
                    size="lg"
                    class="hero-btn q-px-xl"
                    href="mailto:hello@skillsnap.ru"
                    rounded
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

      </q-page>
    </q-page-container>

    <!-- Video Dialog -->
    <q-dialog v-model="videoDialog" maximized>
      <q-card class="video-dialog-card">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6 text-weight-bold">Как это работает</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section class="video-dialog-body" style="height: calc(100vh - 66px); display: flex; align-items: center; justify-content: center; padding: 0 24px 24px;">
          <video
            src=""
            controls
            autoplay
            style="width: 100%; height: 100%; max-height: 85vh; border-radius: 16px; object-fit: contain; background: #000;"
          ></video>
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue';

const videoDialog = ref(false);
const openVideoDialog = () => { videoDialog.value = true; };

const markers = ref([
  'Практика вместо PDF и видео',
  'Быстрый запуск сценариев',
  'Подходит для корпоративного контура и enterprise-внедрения',
]);

const steps = ref([
  {
    title: 'Загружаем материалы',
    desc: 'Скриншоты, инструкции, сценарии — всё, что есть у клиента.',
    gradient: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
  },
  {
    title: 'Система собирает логику симулятора',
    desc: 'ИИ анализирует контент и конструирует интерактивный сценарий.',
    gradient: 'linear-gradient(135deg, #7c3aed, #a21caf)',
  },
  {
    title: 'Пользователь проходит тренировку',
    desc: 'Безопасная среда, пошаговая практика, мгновенная обратная связь.',
    gradient: 'linear-gradient(135deg, #0891b2, #0d9488)',
  },
  {
    title: 'Компания получает результат',
    desc: 'Более быстрое освоение ПО и управляемый, измеримый итог обучения.',
    gradient: 'linear-gradient(135deg, #059669, #16a34a)',
  },
]);

const techList = ref([
  { text: 'ИИ ускоряет сборку сценариев', color: '#4f46e5' },
  { text: 'Симуляторы обучают действием, а не только контентом', color: '#7c3aed' },
  { text: 'Поддерживается работа в enterprise-среде', color: '#0891b2' },
]);

const metrics = ref([
  { value: '1–3 дня', label: 'Time-to-value', color: '#4f46e5' },
  { value: '45 дней', label: 'Time-to-first-simulator', color: '#7c3aed' },
  { value: '60%', label: 'Activation rate', color: '#0891b2' },
  { value: '18%', label: 'Trial-to-paid', color: '#059669' },
  { value: '105–112%', label: 'NRR', color: '#d97706' },
]);

const team = ref([
  {
    name: 'Абарникова Елена',
    role: 'Founder / Product Lead',
    roleColor: '#4f46e5',
    photo: '/team/abarnikova.png',
    bio: 'Опыт в EdTech и e‑learning 20+. Разрабатывала образовательные программы и цифровые курсы для корпоративных клиентов. Отвечает за продуктовую стратегию. Победитель хакатона «Лидеры цифровой трансформации-2024».',
  },
  {
    name: 'Сидорин Тимофей',
    role: 'Co‑founder & CTO (ML / Backend)',
    roleColor: '#0891b2',
    photo: '/team/sidorin.png',
    bio: 'Опыт в машинном обучении и backend‑разработке 3+. Строит ядро ИИ‑моделей, отвечает за серверную часть и надёжность платформы. Призёр хакатона «Лидеры цифровой трансформации 2024 ЯКУТИЯ». Призёр Гагарин Хакатона 2024.',
  },
  {
    name: 'Черненко Константин',
    role: 'CTO (UX/UI / Frontend)',
    roleColor: '#7c3aed',
    photo: '/team/chernenko.png',
    bio: 'UX/UI и frontend‑часть продукта. Опыт проектирования интерфейсов для сложных веб‑приложений 3+. Фокусируется на удобстве для методистов и корпоративных пользователей. Призёр хакатона «Лидеры цифровой трансформации 2024 ЯКУТИЯ».',
  },
]);
</script>

<script>
export default { name: 'LandingPage' };
</script>

<style scoped>
/* ==================== BASE ==================== */
.landing-layout {
  background-color: #ffffff;
  font-family: var(--font-sans);
}
.landing-page {
  min-height: 100vh;
}
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
}
.flex-grow-1 { flex-grow: 1; }

/* ==================== HEADER ==================== */
.landing-header {
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

/* ==================== BG BLOBS ==================== */
.blob-bg {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  z-index: 0;
  opacity: 0.35;
  pointer-events: none;
  animation: blob-float 18s infinite alternate ease-in-out;
}
.blob-1 { top: -8%; left: -8%; width: 50vw; height: 50vw; background: rgba(79, 70, 229, 0.3); }
.blob-2 { top: 35%; right: -10%; width: 40vw; height: 40vw; background: rgba(124, 58, 237, 0.2); animation-delay: -6s; }
.blob-3 { bottom: -10%; left: 10%; width: 55vw; height: 35vw; background: rgba(8, 145, 178, 0.18); animation-delay: -12s; }
@keyframes blob-float {
  0%   { transform: translate(0, 0) scale(1); }
  50%  { transform: translate(4%, 6%) scale(1.05); }
  100% { transform: translate(-3%, 8%) scale(0.95); }
}

/* ==================== TYPOGRAPHY ==================== */
.text-gradient {
  background: linear-gradient(135deg, #4f46e5, #7c3aed, #a21caf);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.section-tag {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: #4f46e5;
  background: rgba(79, 70, 229, 0.08);
  border-radius: 999px;
  padding: 6px 18px;
  margin-bottom: 20px;
}
.section-title {
  font-size: 2.6rem;
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: -0.5px;
  color: #0f172a;
  margin: 0 0 16px;
}
.section-subtitle {
  font-size: 1.1rem;
  color: #64748b;
  max-width: 620px;
  margin: 0 auto;
  line-height: 1.7;
}

/* ==================== HERO ==================== */
.hero-section {
  position: relative;
  z-index: 1;
  padding: 140px 0 100px;
  text-align: center;
}
.hero-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #4f46e5;
  background: rgba(79, 70, 229, 0.08);
  border: 1px solid rgba(79, 70, 229, 0.2);
  border-radius: 999px;
  padding: 8px 20px;
  margin-bottom: 32px;
}
.tag-dot {
  width: 8px; height: 8px;
  background: #4f46e5;
  border-radius: 50%;
  animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.7); }
}
.hero-title {
  font-size: clamp(3rem, 5.5vw, 4.8rem);
  font-weight: 900;
  line-height: 1.05;
  letter-spacing: -2px;
  color: #0f172a;
  margin: 0 0 24px;
}
.hero-subtitle {
  font-size: 1.25rem;
  color: #475569;
  max-width: 680px;
  margin: 0 auto 40px;
  line-height: 1.6;
}
.hero-markers {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px 24px;
  margin-bottom: 48px;
}
.marker-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 500;
  color: #334155;
}
.hero-actions {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 16px;
}
.hero-btn {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.hero-btn:hover { transform: translateY(-3px); }
.hero-btn--primary {
  box-shadow: 0 12px 28px rgba(79, 70, 229, 0.35);
}
.hero-btn--primary:hover {
  box-shadow: 0 16px 36px rgba(79, 70, 229, 0.5);
}
.hero-btn--outline {
  background: white !important;
  border: 1px solid #e2e8f0 !important;
  color: #0f172a !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.hero-btn--outline:hover {
  border-color: #cbd5e1 !important;
  box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}

/* ==================== HOW IT WORKS ==================== */
.section-how {
  position: relative;
  z-index: 1;
  padding: 100px 0;
}
.how-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: start;
}
@media (max-width: 900px) {
  .how-grid { grid-template-columns: 1fr; }
}

/* Before/After card */
.before-after-card {
  padding: 32px;
  display: flex;
  gap: 0;
  align-items: stretch;
}
.ba-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.ba-before { padding-right: 24px; }
.ba-after { padding-left: 24px; }
.ba-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
}
.ba-label {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-radius: 999px;
  padding: 3px 12px;
}
.ba-label--before { background: #fee2e2; color: #dc2626; }
.ba-label--after { background: #d1fae5; color: #059669; }
.ba-icon { font-size: 32px; }
.ba-heading { font-weight: 700; font-size: 15px; color: #0f172a; }
.ba-list {
  margin: 0; padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.ba-list li {
  font-size: 13px;
  color: #64748b;
  padding-left: 16px;
  position: relative;
}
.ba-list li::before {
  content: '—';
  position: absolute;
  left: 0;
  color: #cbd5e1;
}

/* Steps */
.how-right {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.step-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  position: relative;
  padding-bottom: 8px;
}
.step-number {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 800;
  color: white;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}
.step-connector {
  position: absolute;
  left: 21px;
  top: 50px;
  width: 2px;
  height: calc(100% - 8px);
  background: linear-gradient(to bottom, #e2e8f0, transparent);
}
.step-body {
  padding-bottom: 32px;
}
.step-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 6px;
}
.step-desc {
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
}

/* ==================== TECH + METRICS ==================== */
.section-tech {
  position: relative;
  z-index: 1;
  padding: 100px 0;
}
.tech-grid {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 40px;
  align-items: start;
}
@media (max-width: 900px) {
  .tech-grid { grid-template-columns: 1fr; }
}
.tech-left {
  padding: 36px;
}
.tech-block-title {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 28px;
}
.tech-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.tech-list-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  font-size: 15px;
  color: #334155;
  line-height: 1.5;
}
.tech-bullet {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 6px;
}
.tech-right {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
@media (max-width: 600px) {
  .tech-right { grid-template-columns: 1fr; }
}
.metric-card {
  padding: 28px 24px;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.metric-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.08);
}
.metric-value {
  font-size: 2.2rem;
  font-weight: 900;
  letter-spacing: -1px;
  line-height: 1;
  margin-bottom: 8px;
}
.metric-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}
.tech-footer {
  margin-top: 48px;
  text-align: center;
  font-size: 15px;
  color: #94a3b8;
  font-style: italic;
}

/* ==================== TEAM ==================== */
.section-team {
  position: relative;
  z-index: 1;
  padding: 100px 0;
}
.glass-card-solid {
  background: white;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 24px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}
.team-card {
  transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.4s ease;
}
.team-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 30px 60px rgba(0,0,0,0.1) !important;
}
.team-squircle {
  width: 160px; height: 160px;
  border-radius: 36px;
  overflow: hidden;
  border: 4px solid #f1f5f9;
  background-color: #f1f5f9;
}
.team-image {
  width: 100%; height: 100%;
  object-fit: cover;
  object-position: center 10%;
  transition: transform 0.5s ease;
}
.team-card:hover .team-image { transform: scale(1.07); }
.team-role {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}
.desc-text { font-size: 14px; line-height: 1.65; }

/* ==================== CTA ==================== */
.section-cta {
  position: relative;
  z-index: 1;
  padding: 60px 0 100px;
}
.cta-card {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 60%, #a21caf 100%);
  border-radius: 32px;
  padding: 80px 60px;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: 0 30px 60px rgba(79, 70, 229, 0.3);
}
.cta-glow {
  position: absolute;
  top: -60%; left: -20%;
  width: 140%; height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 65%);
  pointer-events: none;
}
.cta-content {
  position: relative;
  z-index: 1;
}
.cta-title {
  font-size: 2.4rem;
  font-weight: 800;
  color: white;
  margin: 0 0 20px;
  letter-spacing: -0.5px;
}
.cta-subtitle {
  font-size: 1.1rem;
  color: rgba(255,255,255,0.8);
  max-width: 560px;
  margin: 0 auto 40px;
  line-height: 1.6;
}
.cta-actions {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 16px;
}

/* ==================== GLASS ==================== */
.glass-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(15, 23, 42, 0.05);
}

/* ==================== ANIMATIONS ==================== */
.animate-fade-in-up {
  animation: fadeInUp 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
  opacity: 0;
  transform: translateY(24px);
}
.animate-stagger-1 { animation-delay: 0.1s; }
.animate-stagger-2 { animation-delay: 0.2s; }
.animate-stagger-3 { animation-delay: 0.35s; }
.animate-stagger-4 { animation-delay: 0.5s; }
@keyframes fadeInUp {
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== VIDEO DIALOG ==================== */
.video-dialog-card {
  border-radius: 16px;
  overflow: hidden;
}
.video-dialog-body {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}
.video-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

/* ==================== RESPONSIVE ==================== */
@media (max-width: 768px) {
  .container { padding: 0 20px; }
  .hero-section { padding: 80px 0 60px; }
  .section-how, .section-tech, .section-team { padding: 60px 0; }
  .section-title { font-size: 2rem; }
  .cta-card { padding: 50px 28px; }
  .cta-title { font-size: 1.8rem; }
  .before-after-card { flex-direction: column; }
  .ba-divider { transform: rotate(90deg); }
  .ba-before { padding-right: 0; padding-bottom: 20px; }
  .ba-after { padding-left: 0; padding-top: 20px; }
}
</style>
