import { useEffect, useState } from 'react';
import Link from 'next/link';
import Head from 'next/head';
import Header from '../components/Header';
import Footer from '../components/Footer';
import ResultsDisplay from '../components/ResultsDisplay';
import { Alert, Loader } from '../components/UI';
import { downloadResume } from '../utils/api';

export default function Results() {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    // Retrieve analysis results from session storage
    const storedResults = sessionStorage.getItem('analysisResults');
    
    if (storedResults) {
      try {
        const data = JSON.parse(storedResults);
        setAnalysisData(data);
      } catch (err) {
        setError('Failed to load analysis results');
      }
    } else {
      setError('No analysis results found. Please start a new analysis.');
    }
    
    setLoading(false);
  }, []);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      // Store the optimized resume data
      const resumeData = {
        optimized_resume: analysisData.optimized_resume,
        original_name: 'optimized_resume'
      };
      
      // Store in session for API call
      sessionStorage.setItem('resumeToDownload', JSON.stringify(resumeData));
      
      await downloadResume(analysisData.optimized_resume || analysisData);
      setError('');
    } catch (err) {
      console.error('Download error:', err);
      setError(err.message || 'Failed to download resume. Please try again.');
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <>
        <Header />
        <main className="section">
          <div className="container" style={{ textAlign: 'center' }}>
            <Loader />
            <p>Loading results...</p>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  if (error && !analysisData) {
    return (
      <>
        <Head>
          <title>Analysis Results - AI Resume Analyzer</title>
        </Head>
        <Header />
        <main className="section">
          <div className="container">
            <Alert message={error} type="error" />
            <div style={{ textAlign: 'center', marginTop: '40px' }}>
              <Link href="/">
                <button className="btn btn-primary btn-lg">← Back to Analyzer</button>
              </Link>
            </div>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Head>
        <title>Analysis Results - AI Resume Analyzer</title>
        <meta name="description" content="View your resume analysis results and download optimized resume" />
      </Head>

      <Header />

      <main className="section">
        <div className="container">
          {error && <Alert message={error} type="error" />}
          
          <div style={{ marginBottom: '30px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
            <h1 style={{ color: 'var(--primary-color)' }}>Analysis Results</h1>
            <Link href="/">
              <button className="btn btn-secondary">← New Analysis</button>
            </Link>
          </div>

          <ResultsDisplay 
            data={analysisData} 
            onDownload={handleDownload}
          />

          {downloading && (
            <div className="card" style={{ textAlign: 'center', padding: '20px', marginTop: '20px', backgroundColor: 'var(--light-bg)' }}>
              <Loader />
              <p>Generating PDF...</p>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </>
  );
}
