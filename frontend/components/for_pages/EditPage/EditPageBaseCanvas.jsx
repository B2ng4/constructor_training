import React from "react";
import ButtonsGroup from "./EditPageDropDown.jsx";

/*
Компонент - весь редактор
*/
function BaseCanvas(props) {
	return (
		<ButtonsGroup props={props}/>
	);
}

export default BaseCanvas;