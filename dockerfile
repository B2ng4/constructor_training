# Этап сборки
FROM node:22 AS build-stage

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и vite.config.js из корня проекта
COPY package*.json ./
COPY vite.config.js ./

# Устанавливаем зависимости
RUN npm install

# Копируем папку frontend (включая src и public)
COPY ./frontend ./frontend

# Проверяем, что файлы скопированы
RUN ls -la /app
RUN ls -la /app/frontend

# Собираем приложение
RUN npm run build

# Проверяем, что сборка прошла успешно
RUN ls -la /app/frontend/public/js  # Проверяем папку, куда собираются файлы

# Этап production
FROM httpd:2.4

# Копируем собранные файлы из папки public/js в Apache
COPY --from=build-stage /app/frontend/public/js /usr/local/apache2/htdocs/js

# Копируем index.html и другие статические файлы
COPY --from=build-stage /app/frontend/public /usr/local/apache2/htdocs/

# Открываем порт 80
EXPOSE 80

# Запускаем Apache
CMD ["httpd-foreground"]