import React, { useState } from 'react';
import { LogIn, UserPlus, Home, Mail, Lock } from 'lucide-react';

// 메인 애플리케이션 컴포넌트
const App = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  // 시뮬레이션된 API 호출 함수
  const handleAuth = (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    
    // 이메일 유효성 검사
    if (!email || !password) {
      setMessage('이메일과 비밀번호를 모두 입력해주세요.');
      setLoading(false);
      return;
    }

    // 간단한 인증/가입 시뮬레이션
    setTimeout(() => {
      setLoading(false);
      if (isLogin) {
        // 로그인 시도 (성공 조건: @success.com)
        if (email.endsWith(' @success.com') && password === '1234') { 
          setMessage(`'${email}'로 로그인 성공! 환영합니다.`);
          console.log('로그인 성공:', email);
        } else {
          setMessage('로그인 실패: 이메일 또는 비밀번호가 올바르지 않습니다.');
        }
      } else {
        // 회원가입 시도
        setMessage(`'${email}'로 회원가입 성공! 이제 로그인해주세요.`);
          console.log('회원가입 성공:', email);
        // 가입 성공 후 입력 필드 초기화 및 로그인 화면으로 자동 전환
        setEmail('');
        setPassword('');
        setIsLogin(true); 
      }
    }, 1500); // 1.5초 지연 시뮬레이션
  };

  const handleHome = () => {
    setMessage('홈 화면으로 이동합니다.');
    console.log('홈으로 이동');
  };

  return (
    // 배경을 옅은 인디고 (bg-indigo-50)으로 변경하여 은은한 색상을 추가
    <div className="min-h-screen bg-indigo-50 flex flex-col items-center justify-center p-4 sm:p-6 font-sans">
      
      {/* 인증 카드: 배경은 흰색 (bg-white)으로 유지하여 깔끔한 대비 제공 *///}
      <div className="w-full max-w-md bg-white rounded-xl shadow-xl p-6 sm:p-8 transition-all duration-300">
        <h1 className="text-3xl font-extrabold text-gray-800 mb-2 text-center">
          {isLogin ? '로그인' : '회원가입'}
        </h1>
        <p className="text-center text-sm text-gray-500 mb-8">
          계정을 이용하여 서비스를 시작해보세요.
        </p>

        {/* 메시지 영역 *///}
        {message && (
          <div 
            className={`p-3 mb-4 text-sm rounded-lg ${message.includes('성공') 
              ? 'bg-green-50 text-green-700 border border-green-200' // 옅은 성공 메시지 배경
              : 'bg-red-50 text-red-700 border border-red-200'       // 옅은 실패 메시지 배경
            }`}
            role="alert"
          >
            {message}
          </div>
        )}

        <form onSubmit={handleAuth} className="space-y-4">
          {/* 이메일 입력 *///}
          <div className="relative">
            <Mail className="absolute top-1/2 left-3 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="email"
              placeholder="이메일 주소"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              // 입력 필드 스타일 유지 (기본 스타일이 옅은 톤에 잘 어울림)
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 ease-in-out"
              disabled={loading}
            />
          </div>

          {/* 비밀번호 입력 *///}
          <div className="relative">
            <Lock className="absolute top-1/2 left-3 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="password"
              placeholder="비밀번호"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 ease-in-out"
              disabled={loading}
            />
          </div>

          {/* 인증 버튼: 인디고(indigo) 계열로 부드러운 느낌 강조 *///}
          <button
            type="submit"
            className="w-full flex items-center justify-center space-x-2 py-3 px-4 border border-transparent rounded-lg shadow-md text-base font-medium text-white bg-indigo-500 hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition duration-150 ease-in-out disabled:opacity-60"
            disabled={loading}
          >
            {loading && (
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            )}
            {!loading && (isLogin ? <><LogIn className="h-5 w-5" /><span>로그인</span></> : <><UserPlus className="h-5 w-5" /><span>회원가입</span></>)}
          </button>
        </form>

        {/* 전환 링크 *///}
        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setMessage('');
              setEmail('');
              setPassword('');
            }}
            // 링크 색상도 인디고 계열로 변경
            className="text-sm font-medium text-indigo-600 hover:text-indigo-500 transition duration-150 ease-in-out"
            disabled={loading}
          >
            {isLogin ? '계정이 없으신가요? 회원가입' : '이미 계정이 있으신가요? 로그인'}
          </button>
        </div>
      </div>

      {/* 홈으로 이동 버튼 *///}
      <div className="mt-8 w-full max-w-md">
        <button
          onClick={handleHome}
          // 홈 버튼을 흰색 배경에 옅은 회색 테두리로 변경하여 부드러운 톤 유지
          className="w-full flex items-center justify-center space-x-2 py-3 px-4 border border-gray-300 rounded-lg shadow-sm text-base font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-300 transition duration-150 ease-in-out disabled:opacity-60"
          disabled={loading}
        >
          <Home className="h-5 w-5" />
          <span>홈으로</span>
        </button>
      </div>

    </div>
  );
};

export default App;
