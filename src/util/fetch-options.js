import { csrfToken } from "./csrf-token"

const fetchOptions = ({body}) => ({
	headers: {
		pragma: 'no-cache',
		'cache-control': 'no-cache',
		'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
		'x-csrftoken': csrfToken
	},
	method: 'POST',
	mode: 'cors',
	credentials: 'include',
	body
})

export default fetchOptions