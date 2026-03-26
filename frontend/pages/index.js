import { useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Header from '../components/Header';
import Footer from '../components/Footer';
import ResumeForm from '../components/ResumeForm';
import { Alert } from '../components/UI';
import { analyzeResume } from '../utils/api';

export default function Home() {
  const router = useRouter();
  const [error, setError] = useState('');

  const handleAnalyze = async (formData) => {
    try {
      setError('');
      const results = await analyzeResume(formData);
      
      // Extract resume and job description text from formData
      let resumeText = '';
      let jobDescription = '';
      
      // Try to read resume file
      if (formData.has('resume_file')) {
        const resumeFile = formData.get('resume_file');
        try {
          resumeText = await resumeFile.text();
        } catch (err) {
          console.warn('Could not read resume file:', err);
        }
      }
      
      // Get job description from formData
      if (formData.has('job_description')) {
        jobDescription = formData.get('job_description');
      } else if (formData.has('job_file')) {
        const jobFile = formData.get('job_file');
        try {
          jobDescription = await jobFile.text();
        } catch (err) {
          console.warn('Could not read job file:', err);
        }
      }
      
      // Store results and context in session storage for results page
      sessionStorage.setItem('analysisResults', JSON.stringify(results));
      sessionStorage.setItem('resumeText', resumeText);
      sessionStorage.setItem('jobDescription', jobDescription);
      
      // Redirect to results page
      router.push('/results');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <>
      <Head>
        <title>AI Resume Analyzer - Optimize Your Resume</title>
        <meta name="description" content="Analyze and optimize your resume using AI" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <Header />

      <main className="section">
        <div className="container">
          {error && <Alert message={error} type="error" />}
          
          <div style={{ maxWidth: '700px', margin: '0 auto' }}>
            <div style={{ textAlign: 'center', marginBottom: '40px' }}>
              <h2 style={{ fontSize: '32px', color: 'var(--primary-color)', marginBottom: '12px' }}>
                AI Resume Analyzer
              </h2>
              <p style={{ fontSize: '16px', color: '#7f8c8d', marginBottom: '8px' }}>
                Get your resume analyzed and optimized for the perfect job match
              </p>
              <p style={{ fontSize: '14px', color: '#95a5a6' }}>
                Our AI will compare your resume with the job description and provide actionable insights
              </p>
            </div>

            <ResumeForm onAnalyze={handleAnalyze} />

            <div className="grid grid-3" style={{ marginTop: '40px' }}>
              <div className="card" style={{ textAlign: 'center', padding: '20px' }}>
                <div style={{ fontSize: '28px', marginBottom: '12px' }}>🎯</div>
                <h4 style={{ marginBottom: '8px' }}>Precise Matching</h4>
                <p style={{ fontSize: '13px', color: '#7f8c8d' }}>
                  AI-powered analysis of job fit
                </p>
              </div>
              <div className="card" style={{ textAlign: 'center', padding: '20px' }}>
                <div style={{ fontSize: '28px', marginBottom: '12px' }}>📊</div>
                <h4 style={{ marginBottom: '8px' }}>Detailed Scores</h4>
                <p style={{ fontSize: '13px', color: '#7f8c8d' }}>
                  Get comprehensive breakdown
                </p>
              </div>
              <div className="card" style={{ textAlign: 'center', padding: '20px' }}>
                <div style={{ fontSize: '28px', marginBottom: '12px' }}>🚀</div>
                <h4 style={{ marginBottom: '8px' }}>Optimization</h4>
                <p style={{ fontSize: '13px', color: '#7f8c8d' }}>
                  Generate improved resume
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </>
  );
}
