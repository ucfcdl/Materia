import React, { useState, useEffect } from 'react'
import { useQuery } from 'react-query'

import { apiGetInstancesFromContext } from '../../util/api'
import { iconUrl as getIconUrl } from '../../util/icon-url'
import LoadingIcon from '../loading-icon'

const PostLogin = () => {
	const [staticURL, setStaticURL] = useState('')
	const [userID, setUserID] = useState(null)
	const [contextID, setContextID] = useState(null)
	const [isAuthor, setIsAuthor] = useState(false)
	const [showAllInstances, setShowAllInstances] = useState(false)

	useEffect(() => {
		waitForWindow().then(() => {
			setStaticURL(window.STATIC_CROSSDOMAIN)
			setContextID(window.CONTEXT_ID)
			setIsAuthor(window.IS_AUTHOR)
			setUserID(parseInt(window.USER_ID))
		})
	}, [])

	const waitForWindow = async () => {
		while (
			!window.hasOwnProperty('STATIC_CROSSDOMAIN') &&
			!window.hasOwnProperty('CONTEXT_ID') &&
			!window.hasOwnProperty('IS_AUTHOR') &&
			!window.hasOwnProperty('USER_ID')
		) {
			await new Promise(resolve => setTimeout(resolve, 500))
		}
	}

	const { isLoading, data: instances } = useQuery({
		queryKey: ['lti-widgets', contextID],
		queryFn: () => apiGetInstancesFromContext(contextID),
		enabled: !!contextID,
		staleTime: Infinity
	})

	let instructor_content = null
	if (!!instances) {
		const instancesRender = instances.map((instance, index) => {

			if (!showAllInstances && instance.has_access) return

			const iconUrl = getIconUrl('/widget/', instance.widget.dir, 92)

			const resource_links = instance.lti_data.map(
				(resource, r_index) => <span key={r_index}>{resource.lti_resource_name}</span>
			)

			return <li key={index} className="instance">
				<img src={iconUrl} alt={instance.name}></img>
				<h3>{instance.name}</h3>
				<section className="instance-quick-links">
					<a href={instance.preview_url} target="_blank">Preview</a>
					<a href={`${window.BASE_URL}my-widgets#${instance.id}`} target="_blank">Manage in Materia</a>
				</section>
				<span className="widget-located-in">This widget is embedded in the following assignments:</span>
				{resource_links}
			</li>
		})
		if ( !!instancesRender) {
			instructor_content = (
				<section className="instructor-instances-empty">
					<div className="instance-view-toggle">
						Test 1
						<label className="toggle-switch">
							<input type="checkbox"></input>
							<span className="slider"></span>
						</label>
						Test 2
					</div>
					There are widgets in your course, but none you have access to. To view them,
					select View All Widgets above.
				</section>
			)
		} else {
			instructor_content = (
				<section className="instructor-instance-list">
					<p>The following widgets are currently detected in your course:</p>
					<ul className="instances">
						{instancesRender}
					</ul>
				</section>
			)
		}
	} else {
		instructor_content = (
			<section>
				Check out some of the resources below to get started with Materia.
				<section className="student-resources">
					<dl>
						<dt><a className="action_button" href='https://www.youtube.com/watch?v=sYrBW7LHOh8' rel="external" target="_blank">Watch Video</a></dt>
						<dd>Watch a quick explainer video to learn more about Materia.</dd>
						<dt><a className="action_button" href={`${window.BASE_URL}/profile`} rel="external" target="_blank">Visit Your Profile</a></dt>
						<dd>Select any widget from the catalog: play the demo to take it for a test drive, then create your own!</dd>
						<dt><a className="action_button" href={`${window.BASE_URL}/help/#instructors`} rel="external" target="_blank">Get Support</a></dt>
						<dd>Visit our help page to see more support resources.</dd>
					</dl>
				</section>
			</section>
		)
	}

	let page_content = null
	if (isAuthor) {
		page_content = (
			<section id="lti-login-section">
				<header id="h1-div">
					<h1>
						Materia: Enhance Your Course with Widgets
					</h1>
				</header>
				<section className="instructor-intro">
					Materia can power-up your course with bite-size, interactive, gamified learning. 
					Select a widget, customize it in minutes, and share it with students. Widgets are great for
					supplemental learning, study aids, and low-stakes assessment. When embedded in your course,
					widgets will automatically sync scores with the gradebook.
				</section>
				{ instructor_content }
			</section>)
	} else {
		page_content = (
			<section id="lti-login-section">
				<header id="h1-div">
					<h1>
						Materia: Interactive Course Content
					</h1>
				</header>
				<section className="student-intro">
					Materia enables students and instructors to create bite-sized interactive pieces of learning content called <em>widgets</em>.
					Your instructor can embed widgets as assignments, study tools, or supplemental learning in your course. As a student, you can make
					widgets too! Use them as study aids or share them with your classmates to help reinforce learning.
				</section>
				<section className="student-resources">
					<dl>
						<dt><a className="action_button" href={`${window.BASE_URL}/catalog`} rel="external" target="_blank">Widget Catalog</a></dt>
						<dd>Browse the widget catalog and create your own!</dd>
						<dt><a className="action_button" href={`${window.BASE_URL}/profile`} rel="external" target="_blank">Visit Your Profile</a></dt>
						<dd>View your Materia play history.</dd>
						<dt><a className="action_button" href={`${window.BASE_URL}/help/#students`} rel="external" target="_blank">Get Support</a></dt>
						<dd>Ran into an issue? Grade didn't sync? We can help.</dd>
					</dl>
				</section>
			</section>)
	}

	return (
		<>
			{ !contextID || isLoading ? <LoadingIcon /> : page_content }
		</>
	)
}

export default PostLogin
