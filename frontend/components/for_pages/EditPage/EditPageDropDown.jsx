import React from "react";
import styles from '@assets/styles/for-components/drop-down.module.css';
import menuIcon from '@assets/img/menu.svg';
import dndStep from '@assets/img/dnd-step.svg';

function DropDown() {
	return (
			<div className={styles['drop-down']}>
				Назад
			</div>
	);
}

function DropDownSteps(props) {
	let styleName = styles['drop-down-step'] + " " + 'q-ml-xl';
	let steps = props.props.props.props.steps.map((step) =>
		<div className={styles.step} key={step.id}>
			<img className={styles['dnd-icon']} src={dndStep} alt="" />
			{step.id}
		</div>
	);
	return (
		<div className={styleName}>
			{steps}
		</div>
	);
}

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