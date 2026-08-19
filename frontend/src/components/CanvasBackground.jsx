import React, { useEffect, useRef } from 'react'

export default function CanvasBackground({ color = 'rgba(217,106,28,0.12)', pointColor = 'rgba(243,241,233,0.12)' }){
  const ref = useRef(null)

  useEffect(()=>{
    const canvas = ref.current
    if(!canvas) return
    const ctx = canvas.getContext('2d')
    let w = canvas.width = canvas.clientWidth
    let h = canvas.height = canvas.clientHeight

    const DPR = window.devicePixelRatio || 1
    canvas.width = w * DPR
    canvas.height = h * DPR
    ctx.scale(DPR, DPR)

    let points = []
    const POINTS = Math.max(12, Math.floor((w*h) / 60000))

    function rand(min, max){ return Math.random()*(max-min)+min }

    for(let i=0;i<POINTS;i++){
      points.push({
        x: rand(0,w),
        y: rand(0,h),
        vx: rand(-0.3,0.3),
        vy: rand(-0.3,0.3),
      })
    }

    let raf = null

    function resize(){
      w = canvas.clientWidth
      h = canvas.clientHeight
      canvas.width = w * DPR
      canvas.height = h * DPR
      ctx.setTransform(DPR,0,0,DPR,0,0)
    }

    window.addEventListener('resize', resize)

    function draw(){
      ctx.clearRect(0,0,w,h)

      // draw lines
      for(let i=0;i<points.length;i++){
        const p = points[i]
        for(let j=i+1;j<points.length;j++){
          const q = points[j]
          const dx = p.x - q.x
          const dy = p.y - q.y
          const dist = Math.sqrt(dx*dx+dy*dy)
          if(dist < Math.min(w,h) * 0.18){
            const alpha = 1 - dist / (Math.min(w,h) * 0.18)
            ctx.strokeStyle = `rgba(217,106,28,${0.06 * alpha})`
            ctx.lineWidth = 1
            ctx.beginPath()
            ctx.moveTo(p.x, p.y)
            ctx.lineTo(q.x, q.y)
            ctx.stroke()
          }
        }
      }

      // draw points
      for(const p of points){
        p.x += p.vx
        p.y += p.vy
        if(p.x < 0 || p.x > w) p.vx *= -1
        if(p.y < 0 || p.y > h) p.vy *= -1
        ctx.fillStyle = pointColor
        ctx.beginPath()
        ctx.arc(p.x, p.y, 1.5, 0, Math.PI*2)
        ctx.fill()
      }

      raf = requestAnimationFrame(draw)
    }

    raf = requestAnimationFrame(draw)

    return ()=>{
      cancelAnimationFrame(raf)
      window.removeEventListener('resize', resize)
    }
  }, [ref])

  return (
    <canvas ref={ref} className="absolute inset-0 pointer-events-none z-0" />
  )
}
