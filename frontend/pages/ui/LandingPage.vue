<template>
  <q-layout view="lHh Lpr lFf" class="bg-grey-1">
    <q-page-container>
      <q-page class="landing-page bg-grey-1">
        <div class="landing-hero row items-center justify-between q-pa-xl q-pb-lg">
          <div class="col-12 col-md-6 landing-hero__left">
            <div class="text-primary text-caption text-weight-medium q-mb-sm">
              Платформа для корпоративного обучения
            </div>
            <div class="text-h3 text-weight-bold q-mb-md">
              Конструктор тренингов,
              <span class="text-primary">который любят методологи</span>
            </div>
            <div class="text-body1 text-grey-7 q-mb-xl">
              Собирайте интерактивные сценарии, проверяйте знания сотрудников и
              анализируйте результаты в единой системе — без разработчиков и сложных настроек.
            </div>
            <div class="row items-center q-gutter-md q-mb-lg landing-hero__actions">
              <q-btn
                unelevated
                rounded
                color="primary"
                label="Начать бесплатно"
                size="lg"
                class="q-px-xl"
                to="/registration"
              />
              <q-btn
                flat
                rounded
                color="primary"
                label="Войти в аккаунт"
                size="lg"
                to="/login"
              />
            </div>
            <div class="row items-center text-grey-6 text-caption q-gutter-sm">
              <q-icon name="verified" color="positive" size="18px" />
              <span>Безопасная авторизация и хранение данных</span>
            </div>
          </div>

          <div class="col-12 col-md-5 landing-hero__right q-mt-lg q-mt-md-none">
            <q-card flat bordered class="landing-preview-card">
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
                  <div class="row items-center q-gutter-xs">
                    <q-icon name="group" size="16px" />
                    <span>До 500 сотрудников</span>
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

          <div class="row q-col-gutter-lg">
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
                    Проектируйте сценарии обучения в виде диаграмм: ветвления,
                    условия, медиа, вопросы и проверки.
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
                    Отслеживайте прогресс, конверсию по шагам и проблемные места
                    в сценариях обучения.
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
                    Раздавайте доступы по ролям и отделам, ограничивайте тренинги
                    по времени и условиям прохождения.
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

.landing-preview-card {
  border-radius: 20px;
  box-shadow: 0 16px 45px rgba(15, 23, 42, 0.12);
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
