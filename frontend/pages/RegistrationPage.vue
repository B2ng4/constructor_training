<template>
    <BaseCard width="500px" title="Регистрация" class="fixed-center">
        <template v-slot:body>
			<q-form
				@submit="onSubmit"
				class="q-gutter-md"
				>
				<q-input
					filled
					v-model="mail"
					hint="Почта"
					lazy-rules
					:rules="[ val => val && val.length > 0 || 'Пожайлуста, введите данные']"
				/>
				<q-input 
					v-model="password" 
					filled type="password" 
					hint="Пароль" 
					lazy-rules
					:rules="[ val => val && val.length > 0 || 'Пожайлуста, введите данные']"
				/>
				<div>
					<q-btn 
						label="Регистрация" 
						type="submit" 
						color="primary" 
						class="full-width"
						/>
					<span 
						class="cursor-pointer text-grey-7 q-mt-sm inline-block q-ml-xs"
						type="reset"
						@click="onReset"
						>
							Очистить
					</span>
				</div>
			</q-form>
		</template>
    </BaseCard>
</template>

<script>
import BaseCard from '../components/BaseComponents/BaseCard.vue';
export default {
    name: 'RegistrationPage',
    components: {BaseCard}
}
</script>

<style scoped>
.my-card :deep(.text-h6) {
	position: absolute;
	top: 10px;
	left: 50%;
	transform: translateX(-50%);
}
</style>