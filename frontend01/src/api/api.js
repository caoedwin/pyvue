// appfront/src/api/api.js
import axiosInstance from './index'

const axios = axiosInstance

export const getBooks = () => {return axios.get(`http://localhost:8000/api/backend01/`)}

export const postBook = (bookName, bookAuthor) => {return axios.post(`http://localhost:8000/api/backend01/`, {'name': bookName, 'author': bookAuthor})}
