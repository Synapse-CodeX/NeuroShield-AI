import { Link, useLocation } from 'react-router-dom';
import {
  ShieldCheck,
  ShieldAlert,
  CheckSquare,
  Search,
  Activity,
} from 'lucide-react';

import './Navbar.css';

const Navbar = () => {
  const location = useLocation();

  const navLinks = [
    {
      path: '/privacy',
      label: 'Privacy',
      icon: ShieldCheck,
    },
    {
      path: '/factcheck',
      label: 'Fact Check',
      icon: CheckSquare,
    },
    {
      path: '/scanner',
      label: 'Scanner',
      icon: Search,
    },
  ];

  return (
    <nav className="navbar">
      <div className="container nav-container">
        <Link to="/" className="nav-logo" aria-label="NeuroShield home">
          <span className="logo-mark">
            <ShieldAlert size={19} strokeWidth={2.2} />
          </span>

          <span className="logo-content">
            <span className="logo-text">NeuroShield</span>
            <span className="logo-subtitle">AI Trust Layer</span>
          </span>
        </Link>

        <div className="nav-links">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.path;

            return (
              <Link
                key={link.path}
                to={link.path}
                className={`nav-link ${isActive ? 'active' : ''}`}
              >
                <Icon size={16} strokeWidth={2.1} />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </div>

        <div className="nav-status">
          <span className="status-indicator">
            <span className="status-dot" />
          </span>

          <span className="status-text">
            <span className="status-label">System</span>
            <span className="status-value">Online</span>
          </span>

          <Activity
            className="status-icon"
            size={15}
            strokeWidth={2}
          />
        </div>
      </div>
    </nav>
  );
};

export default Navbar;