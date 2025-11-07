
import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const handleApiError = (error) => {
  if (error.response) {
    return { error: true, status: error.response.status, data: error.response.data };
  }
  return { error: true, status: 500, data: { detail: 'Unknown error' } };
};

// THEME
export const getTheme = async (userId) => {
  try {
    const response = await axios.get(`${BASE_URL}/settings/advanced/${userId}/theme`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

// LANGUAGE
export const getLanguage = async (userId) => {
  try {
    const response = await axios.get(`${BASE_URL}/settings/advanced/${userId}/language`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

// SECURITY
export const getSecurity = async (userId) => {
  try {
    const response = await axios.get(`${BASE_URL}/settings/advanced/${userId}/security`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export const deleteTheme = async (userId) => {
  try {
    const response = await axios.delete(`${BASE_URL}/settings/advanced/${userId}/theme`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export const deleteLanguage = async (userId) => {
  try {
    const response = await axios.delete(`${BASE_URL}/settings/advanced/${userId}/language`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export const deleteSecurity = async (userId) => {
  try {
    const response = await axios.delete(`${BASE_URL}/settings/advanced/${userId}/security`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};
export const updateTheme = async (userId, theme) => {
  try {
    const response = await axios.put(`${BASE_URL}/settings/advanced/${userId}/theme`, theme);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export const updateLanguage = async (userId, language) => {
  try {
    const response = await axios.put(`${BASE_URL}/settings/advanced/${userId}/language`, language);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export const updateSecurity = async (userId, security) => {
  try {
    const response = await axios.put(`${BASE_URL}/settings/advanced/${userId}/security`, security);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};
// ADVANCED SETTINGS
export const getAdvancedSettings = async (userId) => {
  try {
    const response = await axios.get(`${BASE_URL}/settings/advanced/${userId}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export const updateAdvancedSettings = async (userId, settings) => {
  try {
    const response = await axios.put(`${BASE_URL}/settings/advanced/${userId}`, settings);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export const updateNotifications = async (userId, notifications) => {
  try {
    const response = await axios.put(`${BASE_URL}/settings/advanced/${userId}/notifications`, notifications);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

export const updatePrivacy = async (userId, privacy) => {
  try {
    const response = await axios.put(`${BASE_URL}/settings/advanced/${userId}/privacy`, privacy);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

// Utility: fetch all settings sections in parallel
export const getAllSettingsSections = async (userId) => {
  return Promise.all([
    getTheme(userId),
    getLanguage(userId),
    getSecurity(userId),
    getAdvancedSettings(userId)
  ]);
};
