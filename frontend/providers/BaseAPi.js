import axios from 'axios'

export class BaseApi {
	_baseUrl = '';
	_sourceDomain = '';
	_sourceUrl = '';
	_httpMethod = '';
	_data =  {};
	_params = {};
	_axiosInstance = null;
	_typeContent = null;
	_headers = {};

	constructor(baseUrl) {
		this._baseUrl = baseUrl;
		this._axiosInstance = axios.create({
			baseURL: this.baseUrl,
		});
	}

	set httpMethod(method) {
		let allowedMethods = ['get', 'post', 'put', 'delete', 'patch'];
		if (allowedMethods.includes(method)) {
			this._httpMethod = method;
		} else {
			throw new Error(`Разрешенные методы (${allowedMethods.join(', ')})`);
		}
	}

	get httpMethod() {
		return this._httpMethod;
	}

	set data(data) {
		this._data = data;
	}

	get data() {
		return this._data;
	}

	set params(params) {
		this._params = params;
	}

	get params() {
		return this._params;
	}

	get baseUrl() {
		return this._baseUrl;
	}

	set sourceUrl(sourceUrl) {
		this._sourceUrl = sourceUrl;
	}

	get sourceUrl() {
		return this._sourceUrl;
	}

	get axiosInstance() {
		return this._axiosInstance;
	}

	set sourceDomain(domain) {
		this._sourceDomain = domain;
	}

	get sourceDomain() {
		return this._sourceDomain;
	}

	get headers() {
		return this._headers;
	}

	set headers(headers) {
		this._headers = headers;
	}

	async createRequest() {
		try {
			if (this.axiosInstance) {
				return await this.axiosInstance({
					url: this.baseUrl + this.sourceUrl,
					method: this.httpMethod,
					params: {...this.params},
					data: {...this.data},
					headers: {...this.headers, ...{Authorization: `Bearer ${localStorage.getItem('tokenAuth')}`}}
				});
			}
		} catch (e) {
			return e;
		}
	}
}