import CodeBlockLowlight from "@tiptap/extension-code-block-lowlight";
import { VueNodeViewRenderer } from "@tiptap/vue-3";
import CodeBlockNodeView from "./CodeBlockNodeView.vue";

export const CodeBlockLowlightWithUI = CodeBlockLowlight.extend({
	addNodeView() {
		return VueNodeViewRenderer(CodeBlockNodeView);
	},
});
