import React, { useState, useMemo, useEffect } from 'react'
import MyWidgetScoreSemesterIndividual from './my-widgets-score-semester-individual'
import MyWidgetScoreSemesterStorage from './my-widgets-score-semester-storage'
import MyWidgetScoreSemesterGraph from './my-widgets-score-semester-graph'

const TAB_GRAPH = 'TAB_GRAPH'
const TAB_INDIVIDUAL = 'TAB_INDIVIDUAL'
const TAB_STORAGE = 'TAB_STORAGE'

const MyWidgetScoreSemester = ({semester, instId, hasScores, setInvalidLogin}) => {
	const initData = hasScores ? TAB_GRAPH : TAB_STORAGE
	const [scoreTab, setScoreTab] = useState(initData)

	useEffect(() => {
		if (hasScores) {
			setScoreTab(TAB_GRAPH)
		}
	}, [hasScores, instId])

	const activeTab = useMemo(() => {
		let curTab = scoreTab

		// Tests if there are scores to show
		if ((scoreTab === TAB_INDIVIDUAL || scoreTab === TAB_GRAPH) && hasScores === false) {
			// Has storage data so switch to that
			if (semester.storage) {
				curTab = TAB_STORAGE
				setScoreTab(TAB_STORAGE)
			}
			else {
				curTab = ''
				setScoreTab('')
			}
		}

		switch (curTab) {
			case TAB_GRAPH:
				return <MyWidgetScoreSemesterGraph semester={semester} />

			case TAB_INDIVIDUAL:
				return (
					<MyWidgetScoreSemesterIndividual semester={semester}
						instId={instId} setInvalidLogin={setInvalidLogin}
					/>
				)

			case TAB_STORAGE:
				return (
					<MyWidgetScoreSemesterStorage semester={semester}
						instId={instId} setInvalidLogin={setInvalidLogin}
					/>
				)

			default:
				return null
		}
	}, [scoreTab, semester, hasScores])

	let standardTabElementsRender = null
	if (hasScores) {
		standardTabElementsRender = (
			<>
				<li key={0}
					className={scoreTab === TAB_GRAPH ? 'scoreTypeSelected' : ''}>
					<a className='graph'
						onClick={() => {setScoreTab(TAB_GRAPH)}}>
						Graph
					</a>
				</li>
				<li key={1}
					className={scoreTab === TAB_INDIVIDUAL ? 'scoreTypeSelected' : ''}>
					<a className='table'
						onClick={() => {setScoreTab(TAB_INDIVIDUAL)}}>
						Individual Scores
					</a>
				</li>
			</>
		)
	}

	let storageTabRender = null
	if (semester.storage) {
		storageTabRender = (
			<li key={2}
				className={scoreTab === TAB_STORAGE ? 'scoreTypeSelected' : ''}>
				<a className='data'
					onClick={() => {setScoreTab(TAB_STORAGE)}}>
					Data
				</a>
			</li>
		)
	}

	return (
		<div className='scoreWrapper'>
			<section className='scores-header'>
				<h3 className='semester-label'>{semester.term} {semester.year}</h3>
				<ul className='choices'>
					{ standardTabElementsRender }
					{ storageTabRender }
				</ul>
			</section>
			<section className='scores-tab-content'>
				{ activeTab }
			</section>
		</div>
	)
}

export default MyWidgetScoreSemester
