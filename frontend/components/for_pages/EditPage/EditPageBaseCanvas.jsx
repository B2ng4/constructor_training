import styles from '@assets/styles/for-components/base-canvas.module.css';

function BaseCanvas(props) {
	return (
		<div className="fit">
			<div className={styles['left-button']}>
				<button>Click me</button>
				<button>Click me</button>
			</div>
		</div>
	);
}

export default BaseCanvas;