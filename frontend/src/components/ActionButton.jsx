import React from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'

function ActionButton({
  children,
  to = '/dashboard',
  className = 'btn-primary w-full block text-center flex items-center justify-center gap-2',
  icon = 'fa-arrow-right',
  toastMessage = 'Please log in to continue',
  ...rest
}) {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()

  const handleClick = () => {
    if (isAuthenticated) {
      navigate(to)
    } else {
      toast(toastMessage, { icon: '🔒' })
      navigate('/login')
    }
  }

  return (
    <button onClick={handleClick} className={className} {...rest}>
      {children}
      {icon && <i className={`fas ${icon} text-xs`}></i>}
    </button>
  )
}

export default ActionButton
