// WelcomePage.tsx
import React, { useEffect } from 'react';
import './WelcomePage.css';

const LegalServicePlatform: React.FC = () => {
  useEffect(() => {
    const initParticleEffects = () => {
      const handleMouseMove = (e: MouseEvent) => {
        const particles = document.querySelectorAll('.quantum-particle');
        particles.forEach(particle => {
          const rect = particle.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;
          (particle as HTMLElement).style.setProperty('--x', `${x}px`);
          (particle as HTMLElement).style.setProperty('--y', `${y}px`);
        });
      };

      window.addEventListener('mousemove', handleMouseMove);
      return () => window.removeEventListener('mousemove', handleMouseMove);
    };

    return initParticleEffects();
  }, []);

  return (
      <div className="legal-platform-container">
        {/* 量子粒子背景 */}
        <div className="quantum-particle"></div>
        <div className="quantum-particle"></div>

        {/* 全息投影内容 */}
        <div className="holographic-content">
          <h1 className="platform-title">
            <span>LegalMind--法律文书智能检测系统</span>
            <div className="title-aura"></div>
          </h1>
          {/*<p className="platform-subtitle">基于AI的法律决策支持系统</p>*/}

          {/* 动态服务矩阵 */}
          <div className="service-matrix">
            {[
              {
                name: '法律文书智能审查',
                icon: '⚖️',
                desc: '基于NLP技术自动检测合同风险点，提供合规建议，支持30+法律文书类型'
              },
              {
                name: '法律法规知识图谱',
                icon: '🌐',
                desc: '涵盖百万级法律实体关系，可视化展示法律条文关联性与司法解释'
              },
              {
                name: '智能法律咨询',
                icon: '💬',
                desc: '7×24小时AI法律顾问，婚姻/劳动/合同等9大领域常见问题解答'
              },
              {
                name: '案例智能分析',
                icon: '📊',
                desc: '百万级司法案例数据库，智能提取裁判要点生成可视化分析报告'
              },
              {
                name: '法律智能计算器',
                icon: '🧮',
                desc: '赔偿金/诉讼费/利息智能计算，内置20+法律计算模型，支持自定义参数配置'
              },
              {
                name: '合同风险评估',
                icon: '⚠️',
                desc: '多维度动态量化评估合同风险，生成风险矩阵图与等级评分（AAA-D）'
              }
            ].map((service) => (
                <div key={service.name} className="service-card">
                  <div className="card-inner">
                    {/* 正面内容 */}
                    <div className="card-front">
                      <div className="card-hologram"></div>
                      <div className="card-content">
                        <div className="dynamic-icon">{service.icon}</div>
                        <h3>{service.name}</h3>
                        <div className="card-divider"></div>
                      </div>
                    </div>

                    {/* 背面内容 */}
                    <div className="card-back">
                      <div className="back-content">
                        <p className="card-desc">{service.desc}</p>
                        <div className="legal-stamp">
                          <span>⚖️ LegalMind认证</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
            ))}
          </div>
        </div>
      </div>
  );
};

export default LegalServicePlatform;