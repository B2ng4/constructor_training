<template>
  <q-layout view="lHh Lpr lFf" class="bg-grey-1">
    <q-page-container>
      <q-page class="landing-page bg-grey-1">
        <div class="landing-hero row items-center justify-between q-pa-xl q-pb-lg">
          <div class="col-12 col-md-6 landing-hero__left">
            <div class="hero-badge text-primary text-caption text-weight-medium q-mb-sm animate-fade-in-up">
              Платформа для корпоративного обучения
            </div>
            <div class="text-h3 text-weight-bold q-mb-md hero-title animate-fade-in-up animate-stagger-1">
              Конструктор тренингов,
              <span class="text-primary">который любят все</span>
            </div>
            <div class="text-body1 text-grey-7 q-mb-xl hero-desc animate-fade-in-up animate-stagger-2">
              Собирайте интерактивные сценарии, проверяйте знания сотрудников и
              анализируйте результаты в единой системе — без разработчиков и сложных настроек.
            </div>
            <div class="row items-center q-gutter-md q-mb-lg landing-hero__actions animate-fade-in-up animate-stagger-3">
              <q-btn
                unelevated
                rounded
                color="primary"
                label="Начать бесплатно"
                size="lg"
                class="q-px-xl hero-btn hero-btn--primary"
                to="/registration"
              />
              <q-btn
                flat
                rounded
                color="primary"
                label="Войти в аккаунт"
                size="lg"
                class="hero-btn"
                to="/login"
              />
            </div>

          </div>

          <div class="col-12 col-md-5 landing-hero__right q-mt-lg q-mt-md-none">
            <q-card flat bordered class="landing-preview-card animate-scale-in animate-stagger-4">
              <q-card-section>
                <div class="row items-center justify-between q-mb-md">
                  <div class="text-subtitle1 text-weight-medium">
                    Ваш первый тренинг
                  </div>
                  <q-chip dense color="primary" text-color="white" icon="bolt">
                    Онлайн
                  </q-chip>
                </div>

                <div class="landing-preview-card__graph q-mb-md">
                  <div class="landing-preview-card__node node-main">
                    Вводный сценарий
                  </div>
                  <div class="landing-preview-card__branch">
                    <div class="landing-preview-card__node">Теория</div>
                    <div class="landing-preview-card__node">Практика</div>
                    <div class="landing-preview-card__node">Тестирование</div>
                  </div>
                </div>

                <div class="row items-center justify-between text-caption text-grey-7">
                  <div class="row items-center q-gutter-xs">
                    <q-icon name="timer" size="16px" />
                    <span>Среднее прохождение: 25 минут</span>
                  </div>
                </div>
              </q-card-section>
            </q-card>
          </div>
        </div>

        <div class="landing-features q-px-xl q-pb-xl">
          <div class="text-overline text-primary text-weight-medium q-mb-sm">
            Что внутри платформы
          </div>
          <div class="text-h5 text-weight-bold q-mb-lg">
            Всё, что нужно для полноценного обучения
          </div>

          <div class="row q-col-gutter-lg landing-features-grid animate-stagger-children">
            <div class="col-12 col-md-4">
              <q-card flat bordered class="landing-feature-card">
                <q-card-section>
                  <div class="row items-center q-mb-sm">
                    <q-avatar icon="account_tree" color="primary" text-color="white" />
                    <div class="q-ml-md text-subtitle1 text-weight-medium">
                      Визуальный конструктор
                    </div>
                  </div>
                  <div class="text-body2 text-grey-7">
                    Проектируйте сценарии обучения
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <div class="col-12 col-md-4">
              <q-card flat bordered class="landing-feature-card">
                <q-card-section>
                  <div class="row items-center q-mb-sm">
                    <q-avatar icon="analytics" color="deep-purple" text-color="white" />
                    <div class="q-ml-md text-subtitle1 text-weight-medium">
                      Аналитика и отчёты
                    </div>
                  </div>
                  <div class="text-body2 text-grey-7">
                    Отслеживайте прогресс
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <div class="col-12 col-md-4">
              <q-card flat bordered class="landing-feature-card">
                <q-card-section>
                  <div class="row items-center q-mb-sm">
                    <q-avatar icon="lock" color="teal" text-color="white" />
                    <div class="q-ml-md text-subtitle1 text-weight-medium">
                      Гибкие доступы
                    </div>
                  </div>
                  <div class="text-body2 text-grey-7">
                    Раздавайте доступы, ограничивайте тренинги
                    по времени
                  </div>
                </q-card-section>
              </q-card>
            </div>
          </div>
        </div>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script>
export default {
  name: 'LandingPage',
};
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
}

.landing-hero {
  max-width: 1200px;
  margin: 0 auto;
}

.landing-hero__left {
  max-width: 560px;
}

.hero-badge,
.hero-title,
.hero-desc,
.landing-hero__actions {
  opacity: 0;
}

.hero-btn {
  transition: transform 0.25s var(--anim-ease-spring), box-shadow 0.25s ease, opacity 0.2s ease;
}
.hero-btn:hover {
  transform: translateY(-2px);
}
.hero-btn--primary:hover {
  box-shadow: 0 6px 24px rgba(98, 116, 248, 0.4);
}
.hero-btn:active {
  transform: translateY(0);
}

.landing-preview-card {
  border-radius: 20px;
  box-shadow: 0 16px 45px rgba(15, 23, 42, 0.12);
  transition: box-shadow 0.35s ease, transform 0.35s var(--anim-ease-spring);
}
.landing-preview-card:hover {
  box-shadow: 0 20px 56px rgba(15, 23, 42, 0.14);
  transform: translateY(-4px);
}

.landing-preview-card__graph {
  background: linear-gradient(135deg, #eef2ff, #e0f2fe);
  border-radius: 16px;
  padding: 16px;
}

.landing-preview-card__node {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 14px;
  border-radius: 999px;
  background: white;
  font-size: 13px;
  color: #111827;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
  transition: transform 0.25s var(--anim-ease-spring), box-shadow 0.25s ease;
}
.landing-preview-card:hover .landing-preview-card__node {
  transform: scale(1.02);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.1);
}

.landing-preview-card__node.node-main {
  margin-bottom: 12px;
}

.landing-preview-card__branch {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.landing-features {
  max-width: 1200px;
  margin: 0 auto;
}

.landing-feature-card {
  border-radius: 18px;
  transition: border-color 0.25s ease, box-shadow 0.25s var(--anim-ease-out), transform 0.25s var(--anim-ease-spring);
}
.landing-feature-card:hover {
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.08);
  transform: translateY(-3px);
}
.landing-feature-card :deep(.q-avatar) {
  transition: transform 0.3s var(--anim-ease-spring);
}
.landing-feature-card:hover :deep(.q-avatar) {
  transform: scale(1.08);
}

@media (max-width: 1024px) {
  .landing-hero {
    flex-direction: column;
  }

  .landing-hero__right {
    width: 100%;
  }
}
</style>
