import React from 'react';

const ProfileDropdown = () => {
  return (
    <div className="absolute top-12 right-0 mt-2 w-48 bg-gray-800 rounded-md shadow-lg py-1 z-50">
      <a href="#" className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-700">Your Profile</a>
      <a href="#" className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-700">Settings</a>
      <div className="border-t border-gray-700 my-1"></div>
      <a href="#" className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-700">Sign out</a>
    </div>
  );
};

export default ProfileDropdown; 