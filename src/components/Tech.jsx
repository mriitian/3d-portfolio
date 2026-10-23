import React from 'react'
import { BallsCanvas } from './canvas'
import { sectionwrapper } from '../hoc'
import { technologies } from '../constants/constants'


const Tech = () => {
  return (
    <BallsCanvas icons={technologies.map((technology) => technology.icon)} />
  )
}

export default sectionwrapper(Tech, "")
