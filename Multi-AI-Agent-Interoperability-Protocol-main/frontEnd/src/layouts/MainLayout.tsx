import React from "react";
import { Outlet } from "react-router-dom";
import logoImg from "@/assets/img/logo.png";
import { ModeToggle } from "../components/mode-toggle";

const MainLayout: React.FC = () => {
  return (
    <div className="layout">
      <header className="header">
        <div className="logo">
          <img src={logoImg} alt="logo" />
          <h2>Agent Hive</h2>
        </div>
        <div className="ml-auto">
          <ModeToggle />
        </div>
      </header>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;
