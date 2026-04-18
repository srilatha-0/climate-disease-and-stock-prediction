import '../styles/performance.css';

export default function Performance() {

  // 🔥 DIRECT DATA (your JSON)
  const model1 = {
    name: "Overall Stock Model",
    accuracy: 0.6393120393120393,
    precision: 0.28962264150943395,
    recall: 0.30039138943248533,
    f1: 0.29490874159462055,
    auc: 0.5652726628349538,
    confusion_matrix: [
      [2295, 753],
      [715, 307]
    ]
  };

  const model2 = {
    name: "Dengue Risk Model",
    accuracy: 0.6070275403608737,
    precision: 0.17450232952138925,
    recall: 0.7744360902255639,
    f1: 0.28482544071897686,
    auc: 0.6984899656705676,
    confusion_matrix: [
      [2784, 1949],
      [120, 412]
    ]
  };

  return (
    <div className="performance-page">

      <div className="performance-header">
        <h1>Model Performance</h1>
      </div>

      {/* ===================== */}
      {/* METRICS */}
      {/* ===================== */}
      <div className="metrics-grid">

        <div className="metric-card">
          <h2>{model1.name}</h2>
          <p>Accuracy: {model1.accuracy.toFixed(2)}</p>
          <p>Precision: {model1.precision.toFixed(2)}</p>
          <p>Recall: {model1.recall.toFixed(2)}</p>
          <p>F1 Score: {model1.f1.toFixed(2)}</p>
          <p>AUC: {model1.auc.toFixed(2)}</p>
        </div>

        <div className="metric-card">
          <h2>{model2.name}</h2>
          <p>Accuracy: {model2.accuracy.toFixed(2)}</p>
          <p>Precision: {model2.precision.toFixed(2)}</p>
          <p>Recall: {model2.recall.toFixed(2)}</p>
          <p>F1 Score: {model2.f1.toFixed(2)}</p>
          <p>AUC: {model2.auc.toFixed(2)}</p>
        </div>

      </div>

      {/* ===================== */}
      {/* CONFUSION MATRICES */}
      {/* ===================== */}
      <div className="performance-details">

        <div className="detail-card">
          <h3>{model1.name} - Confusion Matrix</h3>
          <div className="matrix">
            {model1.confusion_matrix.map((row, i) => (
              <div key={i} className="matrix-row">
                {row.map((val, j) => (
                  <div key={j} className="matrix-cell">{val}</div>
                ))}
              </div>
            ))}
          </div>
        </div>

        <div className="detail-card">
          <h3>{model2.name} - Confusion Matrix</h3>
          <div className="matrix">
            {model2.confusion_matrix.map((row, i) => (
              <div key={i} className="matrix-row">
                {row.map((val, j) => (
                  <div key={j} className="matrix-cell">{val}</div>
                ))}
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}