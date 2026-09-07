import { useEffect, useState } from "react";

import api from "../services/api";


function Dashboard() {

  const [data, setData] = useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");


  useEffect(() => {

    api
      .get("/api/dashboard/summary")

      .then((response) => {

        setData(response.data);

        setLoading(false);

      })

      .catch((error) => {

        console.error(error);

        setError(
          "Unable to load dashboard data."
        );

        setLoading(false);

      });

  }, []);


  if (loading) {

    return (
      <div className="page">

        <h1>Loading dashboard...</h1>

      </div>
    );

  }


  if (error) {

    return (
      <div className="page">

        <h1>{error}</h1>

      </div>
    );

  }


  return (

    <div className="page">

      <div className="page-header">

        <h1>TANGLE Dashboard</h1>

        <p>
          Transaction anomaly and governance
          overview
        </p>

      </div>


      <div className="dashboard-grid">

        <div className="card">
          <h3>Total Cases</h3>
          <p>{data.total_cases}</p>
        </div>


        <div className="card">
          <h3>Critical Cases</h3>
          <p>{data.critical_cases}</p>
        </div>


        <div className="card">
          <h3>High Risk Cases</h3>
          <p>{data.high_risk_cases}</p>
        </div>


        <div className="card">
          <h3>Human Review</h3>
          <p>{data.human_review}</p>
        </div>


        <div className="card">
          <h3>Outstanding Balance</h3>

          <p>
            $
            {Number(
              data.outstanding_balance
            ).toLocaleString()}
          </p>
        </div>


        <div className="card">
          <h3>Payment Coverage</h3>

          <p>
            {data.average_payment_coverage}%
          </p>
        </div>


        <div className="card">
          <h3>Resolved / Approved</h3>

          <p>
            {data.resolved_or_approved}
          </p>
        </div>

      </div>

    </div>

  );
}


export default Dashboard;