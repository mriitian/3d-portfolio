import React from 'react'
import { BallCanvas } from './canvas'
import { sectionwrapper } from '../hoc'
import { technologies } from '../constants/constants'


const Tech = () => {
  return (
    <div className='flex flex-row flex-wrap justify-center gap-x-4 gap-y-2 sm:gap-10'>
      {technologies.map((technology) => (
        <div className='w-24 h-24 sm:w-28 sm:h-28' key={technology.name}>
          <BallCanvas icon={technology.icon} />
        </div>
      ))}
    </div>
  )
}

export default sectionwrapper(Tech, "")