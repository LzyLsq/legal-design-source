import React, { useState } from 'react';
import { Upload, message, Card, List, Typography, Alert, Spin, Radio, Button, Space } from 'antd';
import { InboxOutlined, FileExcelOutlined, FileWordOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { saveAs } from 'file-saver';
import { Document, Paragraph, Packer, TextRun } from 'docx';
import { checkCompliance } from '../services/complianceService';
import type { ComplianceResult } from '../types/compliance';
import './CompliancePage.css';

const { Dragger } = Upload;
const { Title, Text } = Typography;

const CompliancePage: React.FC = () => {
  const [results, setResults] = useState<ComplianceResult[]>([]);
  const [isCompliant, setIsCompliant] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);
  const [currentFile, setCurrentFile] = useState<string>('');
  const [provider, setProvider] = useState<string>('openai');

  const exportToCSV = () => {
    if (!results.length) return;

    const csvContent = [
      ['内容', '原因'],
      ...results.map(item => [item.content, item.reason])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8' });
    saveAs(blob, `合规检查结果_${currentFile.replace('.docx', '')}.csv`);
    message.success('CSV导出成功');
  };

  const exportToDocx = async () => {
    if (!results.length) return;

    const doc = new Document({
      sections: [{
        properties: {},
        children: [
          new Paragraph({
            children: [
              new TextRun({
                text: "合规检查结果报告",
                bold: true,
                size: 32,
              }),
            ],
          }),
          new Paragraph({
            children: [new TextRun("")],
          }),
          ...results.flatMap((item, index) => [
            new Paragraph({
              children: [
                new TextRun({
                  text: `问题 ${index + 1}`,
                  bold: true,
                  size: 24,
                }),
              ],
            }),
            new Paragraph({
              children: [
                new TextRun({
                  text: "内容：",
                  bold: true,
                }),
                new TextRun(item.content),
              ],
            }),
            new Paragraph({
              children: [
                new TextRun({
                  text: "原因：",
                  bold: true,
                }),
                new TextRun(item.reason),
              ],
            }),
            new Paragraph({
              children: [new TextRun("")],
            }),
          ]),
        ],
      }],
    });

    const blob = await Packer.toBlob(doc);
    saveAs(blob, `合规检查结果_${currentFile.replace('.docx', '')}.docx`);
    message.success('DOCX导出成功');
  };

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: '.docx',
    showUploadList: true,
    maxCount: 1,
    fileList: currentFile ? [{ uid: '1', name: currentFile, status: 'done' }] : [],
    customRequest: async ({ file }) => {
      if (!(file instanceof File)) return;

      // 清空之前的结果
      setResults([]);
      setIsCompliant(null);
      setCurrentFile(file.name);
      setLoading(true);

      try {
        const response = await checkCompliance(file, provider);
        setResults(response.data.result);
        setIsCompliant(response.data.compliance);
        message.success('文件分析成功');
      } catch (error) {
        message.error('文件分析失败');
        setCurrentFile('');
      } finally {
        setLoading(false);
      }
    },
    onRemove: () => {
      setCurrentFile('');
      setResults([]);
      setIsCompliant(null);
    }
  };

  return (
      <div className="compliance-container">
        {/* 粒子效果背景 */}
        <div className="particles">
          {[...Array(30)].map((_, index) => (
              <div key={index} className="particle"></div>
          ))}
        </div>

        {/* 动态背景层 */}
        <div className="background-patterns">
          <div className="legal-icon legal-icon-scale"></div>
          <div className="legal-icon legal-icon-gavel"></div>
          <div className="legal-icon legal-icon-book"></div>
        </div>

        <div className="compliance-content">
          <Card className="compliance-card">
            <Title level={2} className="compliance-title">法律文书智能审查</Title>

            <div className="provider-selector">
              <Radio.Group value={provider} onChange={e => setProvider(e.target.value)}>
                <Radio.Button value="openai">OpenAI</Radio.Button>
                <Radio.Button value="tongyi">通义法睿</Radio.Button>
              </Radio.Group>
            </div>

            <Dragger {...uploadProps} className="compliance-upload">
              <div className="upload-content">
                <div className="upload-icon">
                  <InboxOutlined />
                  <div className="icon-aura"></div>
                </div>
                <p className="ant-upload-text">点击或拖拽DOCX文件到此区域进行分析</p>
                <p className="ant-upload-hint">
                  仅支持DOCX文件
                </p>
                <div className="legal-icons">
                  <div className="legal-icon legal-icon-scale"></div>
                  <div className="legal-icon legal-icon-gavel"></div>
                  <div className="legal-icon legal-icon-book"></div>
                </div>
              </div>
            </Dragger>

            {loading && (
                <div className="loading-container">
                  <Spin size="large" tip="正在分析文档..." />
                </div>
            )}

            {isCompliant !== null && !loading && (
                <Alert
                    message={isCompliant ? "文档存在合规问题" : "文档通过合规检查"}
                    type={isCompliant ? "warning" : "success"}
                    showIcon
                    className="compliance-alert"
                />
            )}

            {results.length > 0 && (
                <Card
                    title="合规检查结果"
                    className="result-card"
                    extra={
                      <Space>
                        <Button
                            icon={<FileExcelOutlined />}
                            onClick={exportToCSV}
                            type="primary"
                            ghost
                        >
                          导出CSV
                        </Button>
                        <Button
                            icon={<FileWordOutlined />}
                            onClick={exportToDocx}
                            type="primary"
                            ghost
                        >
                          导出DOCX
                        </Button>
                      </Space>
                    }
                >
                  <List
                      dataSource={results}
                      renderItem={(item) => (
                          <List.Item className="result-item">
                            <List.Item.Meta
                                title={item.content}
                                description={
                                  <Text type="secondary">
                                    原因：{item.reason}
                                  </Text>
                                }
                            />
                          </List.Item>
                      )}
                  />
                </Card>
            )}
          </Card>
        </div>
      </div>
  );
};

export default CompliancePage;