import React, { useEffect, useState } from 'react'
import axios from 'axios'

export default function MyCV(){
  const [cvs, setCvs] = useState([])

  useEffect(()=>{
    axios.get('http://localhost:8000/api/cv/', { headers: { Authorization: 'Bearer ' + localStorage.getItem('token') }})
      .then(r=> setCvs(r.data))
      .catch(()=> setCvs([]))
  },[])

  const upload = async (e)=>{
    const file = e.target.files[0]
    if(!file) return
    const form = new FormData()
    form.append('file', file)
    await axios.post('http://localhost:8000/api/cv/upload', form, { headers: { Authorization: 'Bearer ' + localStorage.getItem('token'), 'Content-Type': 'multipart/form-data' }})
    window.location.reload()
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">My CV</h1>
      <input type="file" onChange={upload} />
      <div className="mt-4 space-y-3">
        {cvs.map(cv=> (
          <div key={cv.id} className="panel p-3 rounded">
            <div className="font-semibold">{cv.filename}</div>
            <div className="text-sm text-[rgba(243,241,233,0.6)]">{cv.created_at}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
