import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = React.createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = localStorage.getItem('renzo_user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = (userData) => {
    setUser(userData);
    localStorage.setItem('renzo_user', JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('renzo_user');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Components
const Header = () => {
  const { user, logout } = useAuth();
  const [currentView, setCurrentView] = useState('feed');

  return (
    <header className="bg-gradient-to-r from-blue-50 to-indigo-100 border-b border-blue-200 text-gray-800 p-4 shadow-sm">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-semibold text-indigo-700">🎭 Renzo</h1>
          <p className="text-sm text-gray-600">Turning Passion into Profession</p>
        </div>
        
        {user && (
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-700">Welcome, {user.name}!</span>
            <button
              onClick={logout}
              className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm transition-colors border border-gray-300"
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
};

const Navigation = ({ currentView, setCurrentView }) => {
  const { user } = useAuth();
  
  if (!user) return null;

  const navItems = [
    { key: 'feed', label: '🏠 Feed', icon: '🏠' },
    { key: 'upload', label: '📹 Upload', icon: '📹' },
    { key: 'profile', label: '👤 Profile', icon: '👤' },
    { key: 'discover', label: '🔍 Discover', icon: '🔍' },
    { key: 'connections', label: '🤝 Connections', icon: '🤝' },
  ];

  return (
    <nav className="bg-white shadow-md p-4 sticky top-0 z-10">
      <div className="container mx-auto">
        <div className="flex space-x-6 overflow-x-auto">
          {navItems.map(item => (
            <button
              key={item.key}
              onClick={() => setCurrentView(item.key)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors whitespace-nowrap ${
                currentView === item.key
                  ? 'bg-purple-100 text-purple-700 border-2 border-purple-300'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <span>{item.icon}</span>
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
};

const AuthForm = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    username: '',
    profile_type: 'dancer',
    tags: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const profileTypes = [
    { value: 'dancer', label: '💃 Dancer' },
    { value: 'musician', label: '🎵 Musician' },
    { value: 'director', label: '🎬 Director' },
    { value: 'fan', label: '⭐ Fan' }
  ];

  const tagOptions = [
    'Hip-Hop', 'Classical', 'Contemporary', 'Ballet', 'Jazz',
    'Rock', 'Pop', 'R&B', 'Folk', 'Electronic', 'Vocals', 'Guitar',
    'Piano', 'Drums', 'Beatbox', 'Choreography', 'Freestyle'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        const response = await axios.post(`${API}/auth/login`, {
          email: formData.email,
          password: 'dummy' // MVP: simplified auth
        });
        
        // Get user data
        const userResponse = await axios.get(`${API}/users/${response.data.user_id}`);
        login(userResponse.data);
      } else {
        const response = await axios.post(`${API}/auth/register`, {
          ...formData,
          tags: formData.tags.length > 0 ? formData.tags : ['beginner']
        });
        login(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleTagToggle = (tag) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.includes(tag)
        ? prev.tags.filter(t => t !== tag)
        : [...prev.tags, tag]
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">🎭 Renzo</h1>
          <p className="text-gray-600">Turning Passion into Profession</p>
        </div>

        <div className="flex mb-6">
          <button
            onClick={() => setIsLogin(true)}
            className={`flex-1 py-2 px-4 rounded-l-lg transition-colors ${
              isLogin 
                ? 'bg-purple-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setIsLogin(false)}
            className={`flex-1 py-2 px-4 rounded-r-lg transition-colors ${
              !isLogin 
                ? 'bg-purple-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Register
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <>
              <input
                type="text"
                placeholder="Full Name"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
              <input
                type="text"
                placeholder="Username"
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
              />
            </>
          )}

          <input
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            required
          />

          {!isLogin && (
            <>
              <select
                value={formData.profile_type}
                onChange={(e) => setFormData({...formData, profile_type: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {profileTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  Select Your Skills/Interests:
                </label>
                <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
                  {tagOptions.map(tag => (
                    <label key={tag} className="flex items-center space-x-2 text-sm">
                      <input
                        type="checkbox"
                        checked={formData.tags.includes(tag)}
                        onChange={() => handleTagToggle(tag)}
                        className="text-purple-600 focus:ring-purple-500"
                      />
                      <span>{tag}</span>
                    </label>
                  ))}
                </div>
              </div>
            </>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Processing...' : (isLogin ? 'Login' : 'Create Account')}
          </button>
        </form>
      </div>
    </div>
  );
};

const VideoUpload = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'solo',
    video_data: ''
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef(null);
  const { user } = useAuth();

  const categories = [
    { value: 'solo', label: '🎤 Solo Performance' },
    { value: 'group', label: '👥 Group Performance' },
    { value: 'duet', label: '💫 Duet' },
    { value: 'rehearsal', label: '🎯 Rehearsal' },
    { value: 'performance', label: '🎭 Live Performance' }
  ];

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setFormData(prev => ({
          ...prev,
          video_data: e.target.result
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSuccess(false);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('user_id', user.id);
      formDataToSend.append('title', formData.title);
      formDataToSend.append('description', formData.description);
      formDataToSend.append('category', formData.category);
      formDataToSend.append('video_data', formData.video_data);

      await axios.post(`${API}/videos`, formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setSuccess(true);
      setFormData({
        title: '',
        description: '',
        category: 'solo',
        video_data: ''
      });
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
          📹 Upload Your Performance
        </h2>

        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
            🎉 Video uploaded successfully! AI is processing your content...
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Video Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter a catchy title for your performance"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 h-24 resize-none"
              placeholder="Describe your performance, style, or any special techniques used"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({...formData, category: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {categories.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Video *
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <input
                type="file"
                accept="video/*"
                onChange={handleFileSelect}
                ref={fileInputRef}
                className="hidden"
                required
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="bg-purple-100 text-purple-700 px-6 py-3 rounded-lg hover:bg-purple-200 transition-colors"
              >
                📁 Choose Video File
              </button>
              <p className="text-gray-500 text-sm mt-2">
                Supported formats: MP4, AVI, MOV (Max 100MB)
              </p>
              {formData.video_data && (
                <p className="text-green-600 text-sm mt-2">✅ Video selected</p>
              )}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !formData.video_data}
            className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
          >
            {loading ? '🔄 Processing...' : '🚀 Upload & AI Enhance'}
          </button>
        </form>
      </div>
    </div>
  );
};

const VideoFeed = () => {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    fetchVideos();
  }, []);

  const fetchVideos = async () => {
    try {
      const response = await axios.get(`${API}/videos`);
      setVideos(response.data);
    } catch (err) {
      console.error('Error fetching videos:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async (videoId) => {
    try {
      const formData = new FormData();
      formData.append('user_id', user.id);
      
      const response = await axios.post(`${API}/videos/${videoId}/like`, formData);
      
      // Update local state
      setVideos(prev => prev.map(video => 
        video.id === videoId 
          ? { ...video, likes: video.likes.includes(user.id) 
              ? video.likes.filter(id => id !== user.id)
              : [...video.likes, user.id] 
            }
          : video
      ));
    } catch (err) {
      console.error('Error liking video:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
        🎭 Talent Feed
      </h2>
      
      {videos.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No videos yet. Be the first to upload!</p>
        </div>
      ) : (
        <div className="grid gap-8">
          {videos.map(video => (
            <div key={video.id} className="bg-white rounded-xl shadow-lg overflow-hidden">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                      <span className="text-purple-600 font-bold">
                        {video.user_name.charAt(0)}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-800">{video.user_name}</h3>
                      <p className="text-gray-500 text-sm">@{video.user_username}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm">
                      {video.category}
                    </span>
                    {video.ai_skill_rating && (
                      <span className="bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full text-sm">
                        ⭐ {video.ai_skill_rating.toFixed(1)}
                      </span>
                    )}
                  </div>
                </div>

                <h2 className="text-xl font-bold text-gray-800 mb-2">{video.title}</h2>
                
                {video.description && (
                  <p className="text-gray-600 mb-4">{video.description}</p>
                )}

                <div className="mb-4">
                  <video
                    src={video.video_data}
                    controls
                    className="w-full h-64 object-cover rounded-lg"
                  />
                </div>

                {video.ai_generated_tags.length > 0 && (
                  <div className="mb-4">
                    <div className="flex flex-wrap gap-2">
                      {video.ai_generated_tags.map(tag => (
                        <span key={tag} className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-sm">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <button
                      onClick={() => handleLike(video.id)}
                      className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                        video.likes.includes(user.id)
                          ? 'bg-red-100 text-red-600'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      <span>❤️</span>
                      <span>{video.likes.length}</span>
                    </button>
                    <span className="text-gray-500 text-sm">
                      👁️ {video.views} views
                    </span>
                  </div>
                  <span className="text-gray-400 text-sm">
                    {new Date(video.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const Profile = () => {
  const { user } = useAuth();
  const [userVideos, setUserVideos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserVideos();
  }, []);

  const fetchUserVideos = async () => {
    try {
      const response = await axios.get(`${API}/videos`);
      const myVideos = response.data.filter(video => video.user_id === user.id);
      setUserVideos(myVideos);
    } catch (err) {
      console.error('Error fetching user videos:', err);
    } finally {
      setLoading(false);
    }
  };

  const totalViews = userVideos.reduce((sum, video) => sum + video.views, 0);
  const totalLikes = userVideos.reduce((sum, video) => sum + video.likes.length, 0);
  const avgRating = userVideos.length > 0 
    ? userVideos.reduce((sum, video) => sum + (video.ai_skill_rating || 0), 0) / userVideos.length
    : 0;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
        <div className="text-center mb-6">
          <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-purple-600 font-bold text-2xl">
              {user.name.charAt(0)}
            </span>
          </div>
          <h1 className="text-2xl font-bold text-gray-800">{user.name}</h1>
          <p className="text-gray-500">@{user.username}</p>
          <span className="inline-block bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm mt-2 capitalize">
            {user.profile_type}
          </span>
        </div>

        {user.ai_generated_bio && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">🤖 AI Generated Bio</h3>
            <p className="text-gray-600 bg-gray-50 p-4 rounded-lg">{user.ai_generated_bio}</p>
          </div>
        )}

        {user.tags.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Skills & Interests</h3>
            <div className="flex flex-wrap gap-2">
              {user.tags.map(tag => (
                <span key={tag} className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{userVideos.length}</div>
            <div className="text-gray-500 text-sm">Videos</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{totalViews}</div>
            <div className="text-gray-500 text-sm">Total Views</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{totalLikes}</div>
            <div className="text-gray-500 text-sm">Total Likes</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{avgRating.toFixed(1)}</div>
            <div className="text-gray-500 text-sm">Avg Rating</div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-xl font-bold text-gray-800 mb-6">My Videos</h2>
        
        {loading ? (
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        ) : userVideos.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">No videos uploaded yet. Share your talent!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {userVideos.map(video => (
              <div key={video.id} className="bg-gray-50 rounded-lg p-4">
                <video
                  src={video.video_data}
                  controls
                  className="w-full h-32 object-cover rounded-lg mb-3"
                />
                <h3 className="font-semibold text-gray-800 mb-2">{video.title}</h3>
                <div className="flex justify-between text-sm text-gray-600">
                  <span>❤️ {video.likes.length}</span>
                  <span>👁️ {video.views}</span>
                  <span>⭐ {video.ai_skill_rating?.toFixed(1) || 'N/A'}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const Discover = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      const otherUsers = response.data.filter(u => u.id !== user.id);
      setUsers(otherUsers);
    } catch (err) {
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (userId) => {
    try {
      const formData = new FormData();
      formData.append('from_user_id', user.id);
      formData.append('to_user_id', userId);
      formData.append('message', 'Let\'s collaborate!');

      await axios.post(`${API}/connections`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      alert('Connection request sent!');
    } catch (err) {
      console.error('Error sending connection:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
        🔍 Discover Talent
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {users.map(discoveredUser => (
          <div key={discoveredUser.id} className="bg-white rounded-xl shadow-lg p-6">
            <div className="text-center mb-4">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-purple-600 font-bold text-xl">
                  {discoveredUser.name.charAt(0)}
                </span>
              </div>
              <h3 className="text-lg font-semibold text-gray-800">{discoveredUser.name}</h3>
              <p className="text-gray-500 text-sm">@{discoveredUser.username}</p>
              <span className="inline-block bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm mt-2 capitalize">
                {discoveredUser.profile_type}
              </span>
            </div>

            {discoveredUser.ai_generated_bio && (
              <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                {discoveredUser.ai_generated_bio}
              </p>
            )}

            {discoveredUser.tags.length > 0 && (
              <div className="mb-4">
                <div className="flex flex-wrap gap-1">
                  {discoveredUser.tags.slice(0, 3).map(tag => (
                    <span key={tag} className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs">
                      {tag}
                    </span>
                  ))}
                  {discoveredUser.tags.length > 3 && (
                    <span className="text-gray-500 text-xs">+{discoveredUser.tags.length - 3} more</span>
                  )}
                </div>
              </div>
            )}

            <button
              onClick={() => handleConnect(discoveredUser.id)}
              className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors"
            >
              🤝 Connect
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

const Connections = () => {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    fetchConnections();
  }, []);

  const fetchConnections = async () => {
    try {
      const response = await axios.get(`${API}/connections/${user.id}`);
      setConnections(response.data.connections);
    } catch (err) {
      console.error('Error fetching connections:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
        🤝 My Connections
      </h2>
      
      {connections.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No connections yet. Start discovering talent!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {connections.map(connection => (
            <div key={connection.id} className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                    <span className="text-purple-600 font-bold">
                      {connection.from_user_id === user.id ? 'T' : 'F'}
                    </span>
                  </div>
                  <div>
                    <p className="font-semibold text-gray-800">
                      {connection.from_user_id === user.id ? 'To: ' : 'From: '}
                      Connection Request
                    </p>
                    <p className="text-gray-500 text-sm">
                      {connection.message || 'No message'}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <span className={`inline-block px-3 py-1 rounded-full text-sm ${
                    connection.status === 'accepted' 
                      ? 'bg-green-100 text-green-700'
                      : connection.status === 'rejected'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {connection.status}
                  </span>
                  <p className="text-gray-400 text-xs mt-1">
                    {new Date(connection.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const MainApp = () => {
  const [currentView, setCurrentView] = useState('feed');
  const { user } = useAuth();

  const renderContent = () => {
    switch (currentView) {
      case 'feed':
        return <VideoFeed />;
      case 'upload':
        return <VideoUpload />;
      case 'profile':
        return <Profile />;
      case 'discover':
        return <Discover />;
      case 'connections':
        return <Connections />;
      default:
        return <VideoFeed />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <Navigation currentView={currentView} setCurrentView={setCurrentView} />
      <main className="pb-8">
        {renderContent()}
      </main>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <AuthApp />
      </div>
    </AuthProvider>
  );
}

const AuthApp = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return user ? <MainApp /> : <AuthForm />;
};

export default App;