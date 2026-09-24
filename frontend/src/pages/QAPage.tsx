import React, { useState } from 'react';
import { Input, Button, Card, Spin, message } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import { askQuestion } from '../services/qaService';
import type { QARequest } from '../types/qa';
import './QAPage.css';

const { TextArea } = Input;

const QAPage: React.FC = () => {
  const [question, setQuestion] = useState<string>('');
  const [answer, setAnswer] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    if (!question.trim()) {
      message.error('请输入问题');
      return;
    }

    setLoading(true);
    setAnswer('');

    const request: QARequest = {
      model: 'graphrag-local-search:latest',
      messages: [{ role: 'user', content: question }],
      temperature: 0.7,
    };

    try {
      const response = await askQuestion(request);
      setAnswer(response.choices[0].message.content);
      message.success('回答获取成功');
    } catch (error) {
      message.error('获取回答失败');
    } finally {
      setLoading(false);
    }
  };

  return (
      <div className="qa-container">
        {/* 粒子背景 */}
        <div className="particles">
          {[...Array(20)].map((_, index) => (
              <div key={index} className="particle"></div>
          ))}
        </div>

        {/* 法律条纹背景 */}
        <div className="legal-background"></div>

        {/* 法律图标背景 */}
        <div className="legal-patterns">
          <div className="legal-icon legal-icon-scale"></div>
          <div className="legal-icon legal-icon-book"></div>
        </div>

        <div className="qa-content">
          <Card className="qa-card" title="基于法律知识库的智能法律咨询">
            <div className="input-container">
              <TextArea
                  rows={4}
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="请输入您的法律问题..."
                  className="question-input"
              />
              <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleAsk}
                  className="ask-button"
                  loading={loading}
              >
                {loading ? '加载中...' : '提交问题'}
              </Button>
            </div>
          </Card>

          {loading ? (
              <div className="loading-container">
                <Spin size="large" tip="正在检索法律知识库..." />
              </div>
          ) : (
              answer && (
                  <Card className="answer-card" title="法律建议">
                    <div className="answer-content">{answer}</div>
                  </Card>
              )
          )}
        </div>
      </div>
  );
};

export default QAPage;