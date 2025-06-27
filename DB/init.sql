-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jun 26, 2025 at 02:36 PM
-- Server version: 9.1.0
-- PHP Version: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `navi-bot`
--

-- --------------------------------------------------------

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
CREATE TABLE IF NOT EXISTS `accounts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `accounts`
--

INSERT INTO `accounts` (`id`, `username`, `password`, `name`, `email`, `created_at`) VALUES
(1, 'admin', '$2y$10$axtdiRmEKm.HrO4GGqNWA.e5yG6GcTimie2CznxuDFp0wRmoIwQ/W', 'admin', 'admin@slu.edu.ph', '2025-06-24 01:17:49');

-- --------------------------------------------------------

--
-- Table structure for table `menu_item`
--

DROP TABLE IF EXISTS `menu_item`;
CREATE TABLE IF NOT EXISTS `menu_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `emoji` varchar(10) DEFAULT '',
  `content` text NOT NULL,
  `keywords` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `menu_item`
--

INSERT INTO `menu_item` (`id`, `title`, `emoji`, `content`, `keywords`, `created_at`, `updated_at`) VALUES
(1, 'Admission Policy', '🎓', 'Undergraduate Freshman Students\n\nAll undergraduate freshman applicants must pass the SLU College Entrance Examination (SLU-CEE) and must qualify within the slots duly determined for their chosen course. Registration for the SLU-CEE will be on December or January of the following year. The regular SLU-CEE is conducted during weekends from March up to April. Admission for the first semester starts at the middle of July.\nFor announcements and updates, please visit the SLU-URO Facebook page via https://www.facebook.com/slu.uro .\nTransfer Students\n\nSLU admits transferees in all courses except Bachelor in Medical Laboratory Science subject to their compliance with pertinent requirements and guidelines. They must undergo a Qualifying Examination (QE) and if qualified, will take the Personality Test and Interview. Foreign students applying as transferee are subject to the English Proficiency Test (EPT) rule.\nGraduate Program Students\n\nThe applicant must have f inished the prerequisite degree/s prior to acceptance to the Graduate Program;\nFor a Master’s degree, the applicant must have a Baccalaureate degree from an institution of recognized standing\nFor a Doctorate degree, the applicant must have a Master’s degree in related fields from an institution of recognized standing.\nForeign Students\n\nForeign students should apply not later than 6 months before the start of the academic term. Moreover, they should be in Baguio City at least 4 weeks before the start of classes of the academic term for them to take the EPT as well as SLU-CEE / QE / GPEE, and Personality Test.\nForeign students applying for the first time either in the undergraduate or graduate program should initially possess satisfactory proficiency in English and have passed the EPT as well as the pertinent entrance examination and Personality Test. Before enrolling, they undergo Preadmission Processing at the Student Affairs Office.\nForeign students must secure a valid Student Visa. There are two options in securing a Student Visa. For related information, consult Foreign Student section of the Registrar’s Office.', NULL, '2025-06-24 01:47:17', '2025-06-24 01:47:17'),
(2, 'Admission Requirements', '📋', '`Learn about who can apply and what you need to be eligible.<br>\r\n\r\n<br><strong>Who can apply for the SLU-CEE?</strong><br>\r\n\r\n<br>• Filipino applicants (Grade 12 students or graduates from AY 2023-2024, provided they have not enrolled in college).\r\n<br>• Applicants of good moral character and with no violations in school.\r\n<br>• Filipino applicants from foreign schools should send a scanned transcript and preferred program.\r\n<br>• International students need to process their application at the SLU University Registrar\'s Office and pay a ₱1960 pre-admission fee.\r\n<br>• Persons with disabilities (medical, mental, or psychological) should consult the Director of Counseling and Wellness.\r\n<br>• Alternative Learning System passers must consult the University Registrar before applying.`', NULL, '2025-06-26 14:34:46', '2025-06-26 14:34:46'),
(3, 'Program Catalog', '📚', '`Explore the various programs and courses we offer.<br>\r\n\r\n<br><strong>School of Accountancy, Management, Computing and Information Studies:</strong><br>\r\n<br>&emsp;- Bachelor of Science in Accountancy\r\n<br>&emsp;- Bachelor of Science in Management Accounting\r\n<br>&emsp;- Bachelor of Science in Business Administration Major In:\r\n<br>&emsp;&emsp;- Financial Management with Specialization in Business Analytics\r\n<br>&emsp;&emsp;- Marketing Management with Specialization in Business Analytics\r\n<br>&emsp;- Bachelor of Science in Entrepreneurship\r\n<br>&emsp;- Bachelor of Science in Tourism Management\r\n<br>&emsp;- Bachelor of Science in Hospitality Management\r\n<br>&emsp;- Bachelor of Science in Computer Science\r\n<br>&emsp;- Bachelor of Science in Information Technology\r\n<br>&emsp;- Bachelor of Multimedia Arts<br>\r\n\r\n<br><strong>School of Advanced Studies</strong><br>\r\n<br>&emsp;- Accountancy, Business and Management\r\n<br>&emsp;&emsp;- Doctor of Philosophy in Management\r\n<br>&emsp;&emsp;- Master of Business Administration\r\n<br>&emsp;&emsp;- Master of Entrepreneurship\r\n<br>&emsp;&emsp;- Master of Science in Accountancy\r\n<br>&emsp;&emsp;- Master of Science in Business Administration\r\n<br>&emsp;&emsp;- Master in Financial Technology\r\n<br>&emsp;&emsp;- Master of Science in Public Management\r\n<br>&emsp;- Computing and Information Technology\r\n<br>&emsp;&emsp;- Master in Information Technology\r\n<br>&emsp;&emsp;- Master in Library and Information Science\r\n<br>&emsp;&emsp;- Master of Science in Service, Management, and Engineering\r\n<br>&emsp;- Engineering\r\n<br>&emsp;&emsp;- Doctor of Engineering - Research Track\r\n<br>&emsp;&emsp;- Master in Manufacturing Engineering and Management\r\n<br>&emsp;&emsp;- Master of Arts in Environmental and Habitat Planning\r\n<br>&emsp;&emsp;- Master of Engineering Major in Chemical Engineering\r\n<br>&emsp;&emsp;- Master of Engineering Major in Electrical Engineering\r\n<br>&emsp;&emsp;- Master of Engineering Major in Electronics Engineering\r\n<br>&emsp;&emsp;- Master of Engineering Major in Industrial Engineering\r\n<br>&emsp;&emsp;- Master of Engineering Major in Mechanical Engineering\r\n<br>&emsp;&emsp;- Master of Science in Environmental Engineering\r\n<br>&emsp;&emsp;- Master of Science in Management Engineering\r\n<br>&emsp;&emsp;- Diploma in Disaster Risk Management\r\n<br>&emsp;- Liberal Arts\r\n<br>&emsp;&emsp;- Doctor of Philosophy in Philosophy\r\n<br>&emsp;&emsp;- Doctor of Philosophy in Psychology\r\n<br>&emsp;&emsp;- Master of Arts in Philosophy\r\n<br>&emsp;&emsp;- Master of Arts in Religious Studies\r\n<br>&emsp;&emsp;- Master of Science in Guidance and Counseling\r\n<br>&emsp;&emsp;- Master of Science in Psychology\r\n<br>&emsp;- Natural Sciences\r\n<br>&emsp;&emsp;- Doctor of Philosophy in Biology\r\n<br>&emsp;&emsp;- Doctor of Philosophy in Pharmacy\r\n<br>&emsp;&emsp;- Master in Environmental Sciences\r\n<br>&emsp;&emsp;- Master of Science in Biology\r\n<br>&emsp;&emsp;- Master of Science in Environmental Conservation Biology\r\n<br>&emsp;&emsp;- Master of Science in Medical Technology\r\n<br>&emsp;&emsp;- Master of Science in Medical Technology\r\n<br>&emsp;&emsp;- Master of Science in Pharmacy\r\n<br>&emsp;&emsp;- Master of Science in Public Health\r\n<br>&emsp;&emsp;- Master in Public Health\r\n<br>&emsp;- Nursing\r\n<br>&emsp;&emsp;- Doctor of Philosophy in Nursing - Research Track\r\n<br>&emsp;&emsp;- Master of Science in Nursing\r\n<br>&emsp;&emsp;- Master in Nursing Education\r\n<br>&emsp;- Teacher Education\r\n<br>&emsp;&emsp;- Doctor of Philosophy in Education Major in Science Education\r\n<br>&emsp;&emsp;- Doctor of Philosophy in Educational Management\r\n<br>&emsp;&emsp;- Doctor of Philosophy in Language Education\r\n<br>&emsp;&emsp;- Master of Arts in Catholic Educational Leadership and Management\r\n<br>&emsp;&emsp;- Master of Arts in Education Major in Early Childhood Education\r\n<br>&emsp;&emsp;- Master of Arts in Education Major in Filipino Education\r\n<br>&emsp;&emsp;- Master of Arts in Education Major in Inclusive Education\r\n<br>&emsp;&emsp;- Master of Arts in Education Major in Language Education\r\n<br>&emsp;&emsp;- Master of Arts in Education Major in Mathematics Education\r\n<br>&emsp;&emsp;- Master of Arts in Education Major in Science Education\r\n<br>&emsp;&emsp;- Master of Arts in Education Major in Social Studies\r\n<br>&emsp;&emsp;- Master of Arts in Educational Management\r\n<br>&emsp;&emsp;- Master of Arts in Special Education\r\n<br>&emsp;&emsp;- Master of Science in Physical Education\r\n<br>&emsp;&emsp;- Graduate Certificate in Teaching in Medicine<br>\r\n\r\n<br><strong>School of Engineering and Architecture:</strong><br>\r\n<br>&emsp;- Bachelor of Science in Architecture\r\n<br>&emsp;- Bachelor of Science in Chemical Engineering\r\n<br>&emsp;- Bachelor of Science in Civil Engineering\r\n<br>&emsp;- Bachelor of Science in Electrical Engineering\r\n<br>&emsp;- Bachelor of Science in Electronics Engineering\r\n<br>&emsp;- Bachelor of Science in Geodetic Engineering\r\n<br>&emsp;- Bachelor of Science in Industrial Engineering\r\n<br>&emsp;- Bachelor of Science in Mechanical Engineering\r\n<br>&emsp;- Bachelor of Science in Mechatronics Engineering\r\n<br>&emsp;- Bachelor of Science in Mining Engineering<br>\r\n\r\n<br><strong>School of Law</strong><br>\r\n<br>&emsp;- Juris Doctor (J.D.)\r\n<br>&emsp;- Master of Laws (L.L.M.)<br>\r\n\r\n<br><strong>School of Medicine</strong><br>\r\n<br>&emsp;- Doctor of Medicine<br>\r\n\r\n<br><strong>School of Nursing, Allied Health and Biological Sciences:</strong><br>\r\n<br>&emsp;- Bachelor of Science in Biology\r\n<br>&emsp;- Bachelor of Science in Medical Laboratory Science\r\n<br>&emsp;- Bachelor of Science in Nursing\r\n<br>&emsp;- Bachelor of Science in Pharmacy\r\n<br>&emsp;- Bachelor of Science in Radiologic Technology<br>\r\n\r\n<br><strong>School of Teacher Education and Liberal Arts:</strong><br>\r\n<br>&emsp;- Bachelor of Arts in Communication\r\n<br>&emsp;- Bachelor of Arts in Philosophy\r\n<br>&emsp;- Bachelor of Arts in Political Science\r\n<br>&emsp;- Bachelor of Elementary Education\r\n<br>&emsp;- Bachelor of Physical Education\r\n<br>&emsp;- Bachelor of Science in Psychology\r\n<br>&emsp;- Bachelor of Science in Secondary Education Major In:\r\n<br>&emsp;&emsp;- English\r\n<br>&emsp;&emsp;- Filipino\r\n<br>&emsp;&emsp;- Math\r\n<br>&emsp;&emsp;- Science\r\n<br>&emsp;&emsp;- Social Studies\r\n<br>&emsp;- Bachelor of Special Needs Education\r\n<br>&emsp;- Bachelor of Science in Social Work\r\n<br>&emsp;- Certificate in Teaching`', NULL, '2025-06-26 14:34:46', '2025-06-26 14:34:46'),
(4, 'Tuition & Fees', '💰', '`Find out about the costs for the SLU-CEE and other fees.<br>\r\n\r\n<br><strong>What are the SLU-CEE exam fees?</strong><br>\r\n\r\n<br>• ₱550 for Baguio testing.\r\n<br>• ₱750 for satellite testing.<br>\r\n\r\n<br>&emsp;<em>Note: The fee is non-refundable.</em>`\r\n            },\r\n            \"4\": {\r\n                title: \"Scholarships & Financial Aid\",\r\n                emoji: \"🎓\",\r\n                content: `Discover available scholarships and financial aid options.<br>\r\n\r\n<br><strong>What are the entrance scholarships for SLU-CEE top placers?</strong><br>\r\n\r\n<br>• <b>Top 1-10 placers</b>: 100% tuition fee discount (except miscellaneous fees) for the first semester of AY 2025-2026.\r\n<br>• <b>Top 11-100 placers</b>: 50% tuition fee discount (except miscellaneous fees) for the first semester of AY 2025-2026.<br>\r\n\r\n<br><strong>SLU offers various scholarships:</strong>\r\n<br>• CHED TES / PESFA\r\n<br>• Cebuana Lhuillier Scholarship\r\n<br>• DOST & CHED Graduate Scholarships\r\n<br>• Bukas Tuition Installment Plans`', NULL, '2025-06-26 14:35:50', '2025-06-26 14:35:50'),
(5, 'Enrollment Process', '📝', '`Get detailed, step-by-step instructions on how to apply and enroll.<br>\r\n\r\n<br><strong>How do I apply for the SLU-CEE?</strong><br>\r\n\r\n<br>• Complete the <b>SLU-CEE Application Form</b> online.\r\n<br>• Submit the <b>Principal\'s Recommendation Form</b> and upload it.\r\n<br>• For SHS graduates of AY 2023-2024, submit the <b>Certificate of Non-release of F137a</b>.\r\n<br>• Pay the SLU-CEE Fee: ₱550 for Baguio testing or ₱750 for satellite testing.\r\n<br>• The <b>SLU-CEE Test Permit</b> is valid until August 2025.`', NULL, '2025-06-26 14:35:50', '2025-06-26 14:35:50'),
(6, 'Contact Admissions', '📞', '`Reach out for more info or personalized assistance.<br>\r\n\r\n<br><strong>How can I get in touch with admissions?</strong><br>\r\n\r\n<br>• Email: <b>admissions@slu.edu.ph</b>\r\n<br>• Mobile: <b>09082844467</b><br>\r\n\r\n<br>&emsp;<i>Feel free to reach out for specific questions or issues!</i>`', NULL, '2025-06-26 14:35:50', '2025-06-26 14:35:50');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
