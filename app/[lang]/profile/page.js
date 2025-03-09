const fetchUserProfile = async () => {
  try {
    const response = await axios.get(API_ENDPOINTS.PROFILE, {
      headers: { Authorization: `Bearer ${token}` },
      params: { lang: lang }
    });
    
    if (response.status === 200) {
      setUser(response.data);
    }
  } catch (err) {
    setError(t.error);
  } finally {
    setIsLoading(false);
  }
}; 