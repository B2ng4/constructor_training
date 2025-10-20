<template>
    <div id="vkid-container"></div>
</template>
<script>
export default {
    name: 'vkButoon',
    data() {
        return {
            email: '',
            password: ''
        };
    },
    mounted() {
        if ('VKIDSDK' in window) {
            const VKID = window.VKIDSDK;

            VKID.Config.init({
                app: 53279589,
                redirectUrl: 'https://localhost/personal',
                responseMode: VKID.ConfigResponseMode.Callback,
                source: VKID.ConfigSource.LOWCODE,
                scope: '', // Заполните нужными доступами по необходимости
            });

            const oneTap = new VKID.OneTap();

            oneTap.render({
                container: document.getElementById('vkid-container'), // Указываем контейнер
                showAlternativeLogin: true
            })
            .on(VKID.WidgetEvents.ERROR, this.vkidOnError)
            .on(VKID.OneTapInternalEvents.LOGIN_SUCCESS, (payload) => {
                const code = payload.code;
                const deviceId = payload.device_id;

                VKID.Auth.exchangeCode(code, deviceId)
                    .then(this.vkidOnSuccess)
                    .catch(this.vkidOnError);
            });
        }
    },
    methods: {
        vkidOnSuccess(data) {
            // Обработка полученного результата
            console.log('Успешная авторизация:', data);
        },
        vkidOnError(error) {
            // Обработка ошибки
            console.error('Ошибка авторизации:', error);
        }
    }
};
</script>