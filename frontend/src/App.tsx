import { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import './App.css';
import CompliancePage from './pages/CompliancePage';
import QAPage from './pages/QAPage';
import LegalAgent from './pages/LegalAgent';

const { Header, Content, Sider } = Layout;

function App() {
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const initHeaderEffects = () => {
            const header = document.querySelector('.main-header') as HTMLElement;
            if (header) {
                const handleMouseMove = (e: MouseEvent) => {
                    const rect = header.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    header.style.setProperty('--x', `${x}px`);
                    header.style.setProperty('--y', `${y}px`);
                };

                header.addEventListener('mousemove', handleMouseMove as EventListener);
                return () => {
                    header.removeEventListener('mousemove', handleMouseMove as EventListener);
                };
            }
        };

        return initHeaderEffects();
    }, []);

    const menuItems = [
        {
            key: '/compliance',
            label: '法律文书智能审查',
        },
        {
            key: '/qa',
            label: '智能法律咨询',
        },
        {
            key: '/word',
            label: '法律法规知识图谱',
        },
        {
            key: '/laws',
            label: '法律文书模板',
        },
        {
            key: '/calculate',
            label: '法律智能计算器',
        },
        {
            key: '/RiskAnalysis',
            label: '合同风险评估',
        },
        {
            key: '/exit',
            label: '注销',
        },
    ];

    return (
        <Layout className="layout">
            {/* 顶部固定Header */}
            <Header className="main-header">
                <div className="header-particle" />
                <div className="header-particle" />
                <div className="legal-patterns">
                    <div className="legal-icon legal-icon-scale" />
                    <div className="legal-icon legal-icon-gavel" />
                    <div className="legal-icon legal-icon-book" />
                </div>
                <div className="logo-wrapper">
                    <div className="logo-container">
                        {/* 新增光晕层 */}
                        <div className="logo-orb"></div>

                        {/* 立体文字效果 */}
                        <div className="logo-layers">
                            <div className="logo-backdrop">
                                <span className="legal-text">Legal</span>
                                <span className="mind-text">Mind</span>
                            </div>
                            {/*<div className="logo-foreground">*/}
                            {/*  <span className="legal-text">Legal</span>*/}
                            {/*  <span className="mind-text">Mind</span>*/}
                            {/*</div>*/}
                        </div>

                        {/* 动态粒子效果 */}
                        <div className="logo-particles">
                            <div className="particle particle-1"></div>
                            <div className="particle particle-2"></div>
                            <div className="particle particle-3"></div>
                        </div>

                        {/* 法律图标装饰 */}
                        <div className="logo-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M12 2L9.12 5h5.76L12 2M12 6a3 3 0 0 0-3 3v1h6V9a3 3 0 0 0-3-3m7 3h-1v6l4 4H4l4-4V9H7a5 5 0 0 1-5 5v4h18v-4a5 5 0 0 1-5-5z"/>
                            </svg>
                        </div>
                    </div>
                </div>
            </Header>

            {/* 主体布局 */}
            <Layout style={{ marginLeft: 0 }}>
                {/* 左侧竖向导航栏 */}
                <Sider
                    // 修改侧边栏宽度
                    width={300}
                    className="main-sider"
                    style={{
                        overflow: 'hidden',
                        height: '100vh',
                        position: 'fixed',
                        left: 0,
                        top: 64,
                        background: 'linear-gradient(195deg, rgba(255,255,255,0.96) 0%, rgba(245,242,238,0.96) 100%)',
                    }}
                >
                    <div className="sider-inner">
                        {/* 动态光效层 */}
                        <div className="sider-glow-effect" />

                        {/* 装饰线条 */}
                        <div className="deco-line vertical" />
                        <div className="deco-line horizontal" />

                        {/* 菜单组件 */}
                        <Menu
                            theme="light"
                            mode="vertical"
                            selectedKeys={[location.pathname]}
                            items={menuItems}
                            className="main-menu custom-menu-spacing" // 添加自定义类名
                            onClick={({ key }) => {
                                if (key === '/word') {
                                    window.location.href = 'http://127.0.0.1:5003';
                                } else if (key === '/laws') {
                                    window.location.href = 'http://127.0.0.1:5002';
                                }
                                else if (key === '/calculate') {
                                    window.location.href = 'http://127.0.0.1:5007';
                                }
                                else if (key === '/exit') {
                                    window.location.href = 'http://127.0.0.1:5000';
                                }
                                else if (key === '/RiskAnalysis') {
                                    window.location.href = 'http://127.0.0.1:5020';
                                }
                                else {
                                    navigate(key);
                                }
                            }}
                        />

                        {/* 3D法律图标装饰 */}
                        <div className="legal-3d-icons">
                            <div className="icon-wrap scale-3d">
                                <div className="icon-inner" />
                            </div>
                            <div className="icon-wrap book-3d">
                                <div className="icon-inner" />
                            </div>
                        </div>
                        <div className="legal-dynamic-icons">
                            <div className="law-icon balance"></div>
                            <div className="law-icon book-stack"></div>
                            <div className="law-icon gavel"></div>
                            <div className="law-icon scroll"></div>
                            <div className="law-icon shield"></div>
                        </div>
                    </div>
                </Sider>

                {/* 内容区域 */}
                <Layout
                    style={{
                        // 修改内容区域左外边距
                        marginLeft: 250,
                        paddingLeft: 20,
                        paddingTop: 64, // 顶部留出Header高度
                    }}
                >
                    <Content className="main-content">
                        <Routes>
                            <Route path="/compliance" element={<CompliancePage />} />
                            <Route path="/qa" element={<QAPage />} />
                            <Route path="/" element={<LegalAgent />} />
                        </Routes>
                    </Content>
                </Layout>
            </Layout>
        </Layout>
    );
}

export default App;