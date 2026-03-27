import { BaseApi } from "./BaseAPi.js";

export class CourseApi extends BaseApi {
	constructor() {
		super(__BASE__URL__);
	}

	getCourses() {
		super.params = {};
		super.httpMethod = "get";
		super.sourceUrl = "/course/my_courses";
		return super.createRequest();
	}

	createCourse(payload) {
		super.params = {};
		super.httpMethod = "post";
		super.sourceUrl = "/course/create_course";
		super.data = payload;
		return super.createRequest();
	}

	deleteCourse(courseId) {
		super.params = {};
		super.httpMethod = "delete";
		super.sourceUrl = `/course/${courseId}`;
		return super.createRequest();
	}
}

export const courseApi = new CourseApi();
