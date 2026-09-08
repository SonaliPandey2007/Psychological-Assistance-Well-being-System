import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Cases from "./pages/Cases";
import CaseDetails from "./pages/CaseDetails";
import Victims from "./pages/Victims";
import VictimProfile from "./pages/VictimProfile";
import PriorityCases from "./pages/PriorityCases";
import WelfareFollowUp from "./pages/WelfareFollowUp";
import Analytics from "./pages/Analytics";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<Dashboard />}
        />

        <Route
          path="/cases"
          element={<Cases />}
        />

        <Route
          path="/cases/:caseId"
          element={<CaseDetails />}
        />

        <Route
          path="/victims"
          element={<Victims />}
        />

        <Route
          path="/victims/:victimId"
          element={<VictimProfile />}
        />

        <Route
          path="/priority-cases"
          element={<PriorityCases />}
        />

        <Route
          path="/welfare"
          element={<WelfareFollowUp />}
        />

        <Route
          path="/analytics"
          element={<Analytics />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;