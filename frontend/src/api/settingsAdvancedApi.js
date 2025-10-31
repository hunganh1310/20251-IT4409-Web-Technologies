export const getTheme = async (userId) => {
  const response = await axios.get(`${BASE_URL}/settings/advanced/${userId}/theme`);
  return response.data;
};

export const getLanguage = async (userId) => {
  const response = await axios.get(`${BASE_URL}/settings/advanced/${userId}/language`);
  return response.data;
};

export const getSecurity = async (userId) => {
  const response = await axios.get(`${BASE_URL}/settings/advanced/${userId}/security`);
  return response.data;
};

export const deleteTheme = async (userId) => {
  const response = await axios.delete(`${BASE_URL}/settings/advanced/${userId}/theme`);
  return response.data;
};

export const deleteLanguage = async (userId) => {
  const response = await axios.delete(`${BASE_URL}/settings/advanced/${userId}/language`);
  return response.data;
};

export const deleteSecurity = async (userId) => {
  const response = await axios.delete(`${BASE_URL}/settings/advanced/${userId}/security`);
  return response.data;
};
export const updateTheme = async (userId, theme) => {
  const response = await axios.put(`${BASE_URL}/settings/advanced/${userId}/theme`, theme);
  return response.data;
};

export const updateLanguage = async (userId, language) => {
  const response = await axios.put(`${BASE_URL}/settings/advanced/${userId}/language`, language);
  return response.data;
};

export const updateSecurity = async (userId, security) => {
  const response = await axios.put(`${BASE_URL}/settings/advanced/${userId}/security`, security);
  return response.data;
};
import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const getAdvancedSettings = async (userId) => {
  const response = await axios.get(`${BASE_URL}/settings/advanced/${userId}`);
  return response.data;
};

export const updateAdvancedSettings = async (userId, settings) => {
  const response = await axios.put(`${BASE_URL}/settings/advanced/${userId}`, settings);
  return response.data;
};

export const updateNotifications = async (userId, notifications) => {
  const response = await axios.put(`${BASE_URL}/settings/advanced/${userId}/notifications`, notifications);
  return response.data;
};

export const updatePrivacy = async (userId, privacy) => {
  const response = await axios.put(`${BASE_URL}/settings/advanced/${userId}/privacy`, privacy);
  return response.data;
};
