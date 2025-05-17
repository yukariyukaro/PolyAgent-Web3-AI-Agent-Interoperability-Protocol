import Home from './pages/Home';
import Profile from './pages/Profile';
import MainLayout from './layouts/MainLayout';

export interface AppRoute {
  path: string;
  element: React.ReactNode;
  children?: AppRoute[];
  meta?: {
    title: string;
    icon?: string;
  };
}

export const routes: AppRoute[] = [
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        path: '',
        element: <Home />,
        meta: {
          title: '首页',
        },
      },
      {
        path: 'profile',
        element: <Profile />,
        meta: {
          title: '个人中心',
        },
      },
    ],
  },
]; 