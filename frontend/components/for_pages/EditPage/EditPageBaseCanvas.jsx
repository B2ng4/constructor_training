import styles from '@assets/styles/for-components/base-canvas.module.css';
import menuIcon from '@assets/img/menu.svg';
import React from "react";

function DropDown() {
	return (
		<div className={styles['drop-down']}/>
	);
}

function ButtonsGroup() {
	const [statusDropdown, setStatusDropdown] = React.useState(false);
	return (
		<div className="fit">
			<div className={styles['left-button']}>
				<button onClick={() => setStatusDropdown(!statusDropdown)}>
					<img src={menuIcon} alt="menu" />
				</button>
				<button>
					Страница 1
				</button>
			</div>
			{statusDropdown && <DropDown />}
		</div>
	);
}

function BaseCanvas(props) {
	return (
		<ButtonsGroup/>
	);
}

export default BaseCanvas;