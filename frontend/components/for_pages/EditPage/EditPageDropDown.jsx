import React from "react";
import styles from '@assets/styles/for-components/drop-down.module.css';
import menuIcon from '@assets/img/menu.svg';
import dndStep from '@assets/img/dnd-step.svg';
import add from '@assets/img/add.svg';
import pencil from '@assets/img/pencil.svg';
import check from '@assets/img/check.svg';

/*
	Компонент - выпадающий список
*/
function DropDown() {
	return (
			<div className={styles['drop-down']}>
				Назад
			</div>
	);
}

/*
	Компонент - выпадающий список с шагами
*/
function DropDownSteps(props) {
	//стили
	let styleNameSteps = styles['drop-down-step'] + " " + 'q-ml-xl';
	let styleNameTopBar = styles['top-bar-step'] + " " + 'q-ml-xl';
	let styleStep = styles.step;

	//статус 0
	let iconCheck = <img className={styles['check-icon']} src={check} alt="" />;
	//статус 1
	let iconStepDnd = <img className={styles['dnd-icon']} src={dndStep} alt="" />;
	const [statusMod, setStatusMod] = React.useState(false);

	function handleMod() {
		setStatusMod(!statusMod);
	}

	const [selectedStep, setSelectedStep] = React.useState(props.props.props.props.steps[0]);

	function selectStep(step) {
		return function() {
			setSelectedStep(step);
		}
	}

	let steps = props.props.props.props.steps.map((step) =>
		<div onClick={selectStep(step)} className={styleStep} key={step.id}>
			{statusMod === true ? iconStepDnd : ''}
			{selectedStep === step ? iconCheck : ''}
			<span>{step.id}</span>
		</div>
	);
	return (
		<>
				<div className={styleNameTopBar}>
					<span className="q-ml-md">Шаги</span>
					<div className="q-ml-auto q-gutter-md">
						<img onClick={handleMod} src={pencil} alt="" />
						<img src={add} alt="" className="q-mr-md" />
					</div>
				</div>
				<div className={styleNameSteps}>
					{steps}
				</div>
		</>
	);
}

/*
	Компонент - группа выпадающих списков
*/
function ButtonsGroup(props) {
	const [statusDropdown, setStatusDropdown] = React.useState(false);
	const [statusDropDownStep, setStatusDropDownStep] = React.useState(false);

	return (
		<div className="fit">
			<div className={styles['left-button']}>
				<button
					className={statusDropdown ? styles['button-active'] : ''}
					onClick={() => {setStatusDropdown(!statusDropdown); setStatusDropDownStep(false)}}
				>
					<img src={menuIcon} alt="menu" />
				</button>
				<button
					className={`${styles['button-steps']} ${statusDropDownStep ? styles['button-active'] : ''}`}
					onClick={() => {setStatusDropDownStep(!statusDropDownStep); setStatusDropdown(false)}}
				>
					Страница 1
				</button>
			</div>
			{statusDropdown && <DropDown />}
			{statusDropDownStep && <DropDownSteps props={props}/>}
		</div>
	);
}

export default ButtonsGroup;